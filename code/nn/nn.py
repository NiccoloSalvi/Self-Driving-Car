import torchvision.transforms as transforms
import torch.utils.data as data
import torch.nn as nn
import torchvision
import numpy as np
import cv2 as cv
import torch

num_epoches = 10
num_classes = 10
learning_rate = 0.001
batch_size = 50
input_size = 1024
hidden_layers = 100

class digitRecognizer(nn.Module):
  
  def __init__(self, input_size, hidden_layers, num_classes):
    super(digitRecognizer, self).__init__()
    self.input = nn.Linear(in_features=input_size, out_features=hidden_layers)
    
    self.relu_1 = nn.ReLU()
    self.hidden_1 = nn.Linear(in_features=hidden_layers, out_features=hidden_layers)
    self.relu_2 = nn.ReLU()
    self.hidden_2 = nn.Linear(in_features=hidden_layers, out_features=hidden_layers)
    self.relu_3 = nn.ReLU()
    self.hidden_3 = nn.Linear(in_features=hidden_layers, out_features=hidden_layers)
    self.relu_4 = nn.ReLU()
    
    self.output = nn.Linear(in_features=hidden_layers, out_features=num_classes)

  def forward(self, x):
    model = self.input(x)
    
    model = self.relu_1(model)
    model = self.hidden_1(model)
    model = self.relu_2(model)
    model = self.hidden_2(model)
    model = self.relu_3(model)
    model = self.hidden_3(model)
    model = self.relu_4(model)
    
    model = self.output(model)

    return model

def train():
    if torch.cuda.is_available():
        device = torch.device("cuda")
    else:
        device = torch.device("cpu")

    model = digitRecognizer(input_size, hidden_layers, num_classes)
    repr(model)

    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)

    model = model.to(device)

    BATCH_SIZE = 10
    TRAIN_DATA_PATH = "dataset/train/"
    TEST_DATA_PATH = "dataset/test/"
    TRANSFORM_IMG = transforms.Compose([
        transforms.Resize(32),
        transforms.Grayscale(num_output_channels=1),
        transforms.ToTensor()
    ])

    train_data = torchvision.datasets.ImageFolder(root=TRAIN_DATA_PATH, transform=TRANSFORM_IMG)
    train_data_loader = data.DataLoader(train_data, batch_size=BATCH_SIZE, shuffle=True, num_workers=2)
    test_data = torchvision.datasets.ImageFolder(root=TEST_DATA_PATH)
    test_data_loader  = data.DataLoader(test_data, batch_size=BATCH_SIZE, shuffle=True, num_workers=2) 

    checkdata = iter(train_data_loader)
    img, lab = next(checkdata)
    print(img.shape, lab.shape)

    print("Number of train samples: ", len(train_data))
    print("Number of test samples: ", len(test_data))
    print("Detected Classes are: ", train_data.class_to_idx) # classes are detected by folder structure

    for epoch in range(num_epoches):        
        for step, (images, labels) in enumerate(train_data_loader):
            images = images.reshape(-1, 32*32).to(device)
            labels = labels.to(device)

            outputs = model(images)
            loss = criterion(outputs, labels)

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            print("Epoch: {}/{}, step: {}/{}, loss: {:.4f}".format(epoch, num_classes, step, len(train_data), loss.item()))

    torch.save(model.state_dict(), "myModel.pt")

def test():
    net = digitRecognizer(1024, 100, 10)
    net.load_state_dict(torch.load("myModel.pt"))
    
    if torch.cuda.is_available():
        device = torch.device("cuda")
    else:
        device = torch.device("cpu")

    net = net.to(device)

    image = cv.imread("test\\9.jpg")
    gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    res = cv.resize(gray, (32, 32))
    
    tens = transforms.ToTensor()(res)
    images = tens.reshape(-1, 32*32).to(device)
    outputs = net(images)
    _, predicted = torch.max(outputs, 1)

    print("Predictions: ")
    for out in range(len(outputs[0])):
        print("\t" + str(out) + ": " + str(outputs[0][out].item()))
    
    print("Max predicted: {}".format(predicted.item()))

    cv.imshow("image", image)
    cv.waitKey(0)

if __name__ == '__main__':
    # train()

    test()