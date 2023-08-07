import os
from unittest import result
import uuid
from shutil import rmtree
import cv2
from datetime import date
from fastapi import UploadFile
from ultralytics import YOLO
from app.ovitrampa.models import Images, Segments
from tortoise.functions import Sum

# def save_result_predict()


def count_objects(result, model_classes):
    object_counts = {x: 0 for x in model_classes}

    for c in result.boxes.cls:
        c = int(c)
        if c in model_classes:
            object_counts[c] += 1
        elif c not in model_classes:
            object_counts[c] = 1

    objects_counts = {}
    for i in object_counts:
        objects_counts[model_classes[i]] = object_counts[i]

    return objects_counts


async def predict(source_dir: str, destination_dir: str, image_id: int):

    neutal_network_dir = os.path.join(os.getcwd(), "neural_network")

    if os.path.isfile(f"{neutal_network_dir}/best.pt"):
        model = YOLO(f"{neutal_network_dir}/best.pt")
    else:
        raise Exception("neural network not found")

    files_names = os.listdir(source_dir)

    files_names = [
        file
        for file in os.listdir(source_dir)
        if os.path.isfile(f"{source_dir}/{file}")
    ]

    list_files = [f"{source_dir}/{file}" for file in files_names]

    results = model.predict(list_files, conf=0.41)

    index = 0

    segments = []

    for result in results:

        objects_counts = count_objects(result, model.names)

        img = result.plot()
        cv2.imwrite(f"{destination_dir}/{files_names[index]}", img)

        segment = await Segments(
            file_name=f"{files_names[index]}",
            eggs=objects_counts["egg"],
            bad_eggs=objects_counts["bad_egg"],
            imagem_id=image_id
        )
        await segment.save()
        index += 1
        segments.append(segment)

    return segments


def slice_image(path_origin: str, path_dest: str, file_name: str):
    width = 640
    height = 640

    if os.path.isfile(f"{path_origin}/{file_name}"):
        base, ext = os.path.splitext(file_name)

        if not os.path.isdir(path_dest):
            os.mkdir(path_dest)

        img = cv2.imread(f"{path_origin}/{file_name}")
        index_x = 0
        for x in range(0, img.shape[0], width):
            index_y = 0
            for y in range(0, img.shape[1], height):
                cv2.imwrite(
                    f"{path_dest}/{base}_{index_x}{index_y}{ext}",
                    img[x: x + width, y: y + height, :],
                )
                index_y += 1
            index_x += 1


def thumbnail_image(path_origin: str, path_dest: str, file_name: str):
    width = 640
    height = 360

    if os.path.isfile(f"{path_origin}/{file_name}"):
        base, ext = os.path.splitext(file_name)

        if not os.path.isdir(path_dest):
            os.mkdir(path_dest)

        img = cv2.imread(f"{path_origin}/{file_name}")

        ratio = 640.0 / img.shape[1]
        dimension = (640, int(img.shape[0] * ratio))

        imRes = cv2.resize(img, dimension, interpolation=cv2.INTER_LINEAR)

        cv2.imwrite(f"{path_dest}/{file_name}", imRes)


def create_struct(file_dir: str):
    storage_dir = os.path.join(os.getcwd(), "storage")
    if not os.path.exists(storage_dir):
        os.makedirs(storage_dir)

    original_dir = os.path.join(storage_dir, "original")
    if not os.path.exists(original_dir):
        os.makedirs(original_dir)

    processed_dir = os.path.join(storage_dir, "processed")
    if not os.path.exists(processed_dir):
        os.makedirs(processed_dir)

    predict_dir = os.path.join(storage_dir, "predict")
    if not os.path.exists(processed_dir):
        os.makedirs(processed_dir)

    thumbnail_dir = os.path.join(storage_dir, "thumbnail")
    if not os.path.exists(thumbnail_dir):
        os.makedirs(thumbnail_dir)

    original_file_dir = os.path.join(original_dir, file_dir)
    if not os.path.exists(original_file_dir):
        os.makedirs(original_file_dir)

    processed_file_dir = os.path.join(processed_dir, file_dir)
    if not os.path.exists(processed_file_dir):
        os.makedirs(processed_file_dir)

    predict_file_dir = os.path.join(predict_dir, file_dir)
    if not os.path.exists(predict_file_dir):
        os.makedirs(predict_file_dir)

    thumbnail_file_dir = os.path.join(thumbnail_dir, file_dir)
    if not os.path.exists(thumbnail_dir):
        os.makedirs(thumbnail_dir)

    return {
        "original_dir": original_dir,
        "processed_dir": processed_dir,
        "predict_dir": predict_dir,
        "original_file_dir": original_file_dir,
        "processed_file_dir": processed_file_dir,
        "predict_file_dir": predict_file_dir,
        "thumbnail_dir": thumbnail_dir,
        "thumbnail_file_dir": thumbnail_file_dir
    }


async def storage(date: date, files: list[UploadFile], cycle_id: int):
    results = []

    for file in files:
        try:
            base, ext = os.path.splitext(file.filename)
            contents = file.file.read()
            hash = str(uuid.uuid4())[:8]
            file_dir = str(date) + "-" + hash
            paths = create_struct(file_dir=file_dir)
            file_name = f"{file_dir}{ext}"
            with open(f"{paths['original_file_dir']}/{file_name}", "wb") as f:
                f.write(contents)

            thumbnail_image(
                path_origin=paths["original_file_dir"],
                path_dest=paths["thumbnail_file_dir"],
                file_name=file_name,
            )

            slice_image(
                path_origin=paths["original_file_dir"],
                path_dest=paths["processed_file_dir"],
                file_name=file_name,
            )

            cycle_image = await Images(
                file_name=file_dir,
                file_extension=ext,
                cycle_id=cycle_id
            )
            await cycle_image.save()

            segments = await predict(
                paths["processed_file_dir"],
                paths["predict_file_dir"],
                image_id=cycle_image.id
            )
            
            results.append(cycle_image)
        except Exception:
            return {"message": "There was an error uploading the file(s)"}
        finally:
            file.file.close()

    return results


def delete(image: Images):
    try:
        storage_dir = os.path.join(os.getcwd(), "storage")
        original_dir = os.path.join(storage_dir, "original")
        processed_dir = os.path.join(storage_dir, "processed")
        predict_dir = os.path.join(storage_dir, "predict")

        original_file_dir = os.path.join(original_dir, image.file_name)
        processed_file_dir = os.path.join(processed_dir, image.file_name)
        predict_file_dir = os.path.join(predict_dir, image.file_name)

        rmtree(original_file_dir, onerror=True)
        rmtree(processed_file_dir, onerror=True)
        rmtree(predict_file_dir, onerror=True)
        return True
    except Exception:
        return False
