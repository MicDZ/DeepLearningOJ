import os
import signal
import PIL.Image as Image
import torch
from torchvision.transforms import transforms


from celery import shared_task
from .models import ModelScore, FileUpload


class TimeoutException(Exception):
    pass


def timeout_handler(signum, frame):
    raise TimeoutException


def predict(model, img_path, device):
    img = Image.open(img_path).convert('L')
    img = transforms.ToTensor()(img)
    img = img.unsqueeze(0)
    img = img.to(device)
    result = model(img)
    if result.shape[1] != 10:
        return 'Error', '输出维度不为10'
    pred = result.argmax(dim=1, keepdim=True)

    return pred.item()


def evaluate(model, folder_path, device):
    correct = list(0. for i in range(10))
    total = list(0. for i in range(10))

    # Set alarm before the loop
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(1)  # Set evaluation time limit here (in seconds)

    try:
        for img_file in os.listdir(os.path.join(folder_path, 'images')):
            img_path = os.path.join(folder_path, 'images', img_file)
            label_path = os.path.join(folder_path, 'labels', img_file.replace('.jpg', '.txt'))

            with open(label_path, 'r') as f:
                label = int(f.read().strip())

            pred = predict(model, img_path, device)

            # Handle error
            if type(pred) == tuple and pred[0] == 'Error':
                return pred

            if pred == label:
                correct[label] += 1
            total[label] += 1
    except TimeoutException:
        return 'Error', 'Evaluation Time Limit Exceeded'

    finally:
        signal.alarm(0)

    scores = [f'{int(correct[i])}/{int(total[i])}' for i in range(10)]
    overall_score = sum(correct) / sum(total)

    return 'Correct', (scores, overall_score)


@shared_task(bind=True, expires=60)
def score_model(self, file_id):
    device_mode = "cpu"

    device = torch.device(device_mode)
    print("in judgeing")


    model_path = str(ModelScore.objects.get(id=file_id).file.path)

    print(model_path, device)
    try:
        model = torch.jit.load(model_path, map_location=device)
    except:
        ModelScore.objects.filter(id=file_id).update(status='Load Model Error', score=0)
        return
    # model.eval()
    # model.to(device)
    folder_path = './test_data/handwritten_ocr'
    status, content = evaluate(model, folder_path, device)

    score = 0
    if status == 'Correct':
        # for i in range(10):
        # print(f'{i}: {content[0][i]}')
        score = content[1]
        info = "Success"
    elif status == 'Error':
        score = 0
        info = content

    ModelScore.objects.filter(id=file_id).update(score=score * 100, status=info)
    return