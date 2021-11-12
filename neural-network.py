# -*- coding: utf-8 -*-
"""stat430progressreport.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1kR6du6YZYArmTpvC6ch7yDbq3-TWUrDr
"""

from bs4 import BeautifulSoup
import requests
import shutil

page = requests.get('https://www.justwatch.com/us/provider/netflix')
soup = BeautifulSoup(page.content, 'html.parser')

main_page_lists = soup.find('div', class_='title-list-grid')
imgs = main_page_lists.find_all('img')
shows_grid = main_page_lists.find_all('div', 'title-list-grid__item')

for img in imgs:
  img_url = ''
  try:
    img_url = img['data-src']
  except:
    img_url = img['src']
  r = requests.get(img_url)
  r.raw.decode_content = True
  with open(img['alt'].replace(' ', '-')+'.jpeg', 'wb') as f:
    f.write(r.content)

actual_ratings = []

for div in shows_grid:
  r = requests.get('https://www.justwatch.com'+ div.find('a')['href'])
  soup2 = BeautifulSoup(r.content, 'html.parser')
  rating_div = soup2.find('div', class_='jw-scoring-listing__rating')
  percentage = rating_div.find('a').get_text()
  actual_ratings.append(int(percentage[1:3]))
  # print(rating_div.find('a').get_text())


#Images have Dimensions 166 x 236

actual_ratings

import glob
import numpy as np
from PIL import Image

filelist = glob.glob('*.jpeg')

images = np.array([np.array(Image.open(fname)) for fname in filelist])

images.shape[0]

import torch
import torchvision
from torchvision import transforms
from torchvision.datasets import ImageFolder

from sklearn.model_selection import train_test_split

#np.shape(images)

# Here, we split the data into training and test sets

training_images, test_images, training_ratings, test_ratings = train_test_split(images, actual_ratings, test_size = .3)

np.shape(training_images)
training_images = training_images.transpose(0, 3, 1, 2)

np.shape(training_images)
# np.shape(training_ratings)
# np.shape(test_images)
# np.shape(test_ratings)

# Here, we convert the images from numpy arrays to PyTorch Tensors

training_images = torch.from_numpy(training_images)
test_images = torch.from_numpy(test_images)



#training_images = torch.tensor(training_images, dtype = torch.long)
print(training_images.shape)

type(training_images)

import matplotlib.pyplot as plt

# Here's how to see what the first training image looks like

# plt.imshow(training_images[0])

# # Here, we set up our reporting mechanism, such as calculating our losses and how to present the overall loss and accuracy for each epoch.

# class ImageClassificationTV(nn.Module):
  
#   def training_step(self, values):
#     images = values
#     output = self(images)
#     loss = F.cross_entropy(out, training_ratings)
#     return loss

#   def validation_step(self, values):
#     images = values
#     out = self(images)
#     loss = F.cross_entropy(out, test_ratings)
#     test_accuracy = accuracy(out, test_ratings)
#     return {'loss_value': loss.detach(), 'accuracy_value': test_accuracy}

#   def end_of_epoch_validation(self, outputs):
#     overall_loss = [i['loss_value'] for i in outputs]
#     loss_epoch = torch.stack(overall_loss).mean()

#     overall_accuracy = [i['accuracy_value'] for i in outputs]
#     accuracy_epoch = torch.stack(overall_accuracy).mean()

#     return {'epoch_loss': loss_epoch.item(), 'epoch_accuracy': accuracy_epoch.item()}

#   def end(self, epoch, result):
#     print("Epoch [{}], train_loss: {:.4f}, loss_value: {:.4f}, accuracy_value: {:.4f}".format(epoch, result['train_loss'], result['epoch_loss'], result['epoch_accuracy']))

# Here, we actually define the CNN and what layers it contains.

import torch.nn as nn
import torch.nn.functional as F

class RatingClassification(nn.Module):
  def __init__(self):
    super(RatingClassification, self).__init__()

    self.layer1 = nn.Conv2d(in_channels=3, out_channels=32, kernel_size=6, stride=1, padding=2)
    self.layer2 = nn.ReLU()
    self.layer4 = nn.Conv2d(in_channels = 32, out_channels=64, kernel_size=3, stride=1, padding=2)
    self.layer5 = nn.ReLU()
    self.layer6 = nn.MaxPool2d(kernel_size=2, stride=2)
    self.layer7 = nn.Flatten()
    self.layer8 = nn.Linear(in_features=626816, out_features=512)
    self.layer9 = nn.ReLU()
    self.layer10 = nn.Linear(in_features=512, out_features=10)
    self.layer11 = nn.ReLU(),
    self.layer12 = nn.Linear(128, 64),
    self.layer13 = nn.ReLU(),
    self.layer14 = nn.Linear(64, 10),
    self.layer15 = nn.Softmax()

  def forward(self, x):
    x = F.conv2d(input=x, weight=torch.randn(32, 3, 4, 4), stride=1, padding=2)
    #x = F.relu(self.layer1(x))
    x = F.relu(self.layer2(x))
    x = F.conv2d(input=x, weight=torch.randn(64, 32, 6, 6), stride=1, padding=2)
    x = F.relu(self.layer5(x))
    x = self.layer6(x)
    x = self.layer7(x)
    x = self.layer8(x)
    x = F.relu(self.layer9(x))
    x = self.layer10(x)
    x = F.relu(x)
#    x = self.layer12(x)
    # x = F.relu(self.layer13(x))
    # x = self.layer14(x)
    x = F.log_softmax(x)
    
    return x

train_CNN = RatingClassification()
training_images = training_images.type(dtype=torch.FloatTensor)
print(training_images.shape)
print(type(training_images))
y = train_CNN(training_images)

print(y[0])

predicted_ratings = y.detach().numpy()

predicted_ratings = predicted_ratings / 1000

predicted_ratings = np.abs(predicted_ratings)

predictions = predicted_ratings.sum(axis = 1)

loss_value = training_ratings - predictions

loss_value