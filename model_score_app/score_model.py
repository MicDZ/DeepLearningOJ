import os
import signal
import PIL.Image as Image
import torch
from torchvision.transforms import transforms


from celery import shared_task
from .models import ModelScore


class TimeoutException(Exception):
    pass


def timeout_handler(signum, frame):
    raise TimeoutException


def predict(model, img_path, device):
    img = Image.open(img_path).convert('L')
    img = transforms.ToTensor()(img)
    img = img.unsqueeze(0)
    img = img.to(device)
    try:
        result = model(img)
    except:
        return 0, 'Input Error'
    if result.shape[1] != 10:
        return 0, 'Output Error'
    pred = result.argmax(dim=1, keepdim=True)

    return pred.item(), 'Success'


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

            pred, status = predict(model, img_path, device)

            # Handle error
            if type(pred) == tuple and pred[0] != 'Success':
                return pred

            if pred == label:
                correct[label] += 1
            total[label] += 1
    except TimeoutException:
        return 'Evaluation Time Limit Exceeded', 0

    finally:
        signal.alarm(0)

    scores = [f'{int(correct[i])}/{int(total[i])}' for i in range(10)]
    overall_score = sum(correct) / sum(total)

    return 'Success',  overall_score, correct


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
    status, score, detail_scores = evaluate(model, folder_path, device)
    ModelScore.objects.filter(id=file_id).update(score=score * 100, status=status)
    ModelScore.objects.filter(id=file_id).update(class0=detail_scores[0], class1=detail_scores[1], class2=detail_scores[2], class3=detail_scores[3], class4=detail_scores[4], class5=detail_scores[5], class6=detail_scores[6], class7=detail_scores[7], class8=detail_scores[8], class9=detail_scores[9])
    return