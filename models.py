import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

"""
Implementation of 3D CNN.
"""
class CNN3D(nn.Module):
    def __init__(self, img_depth=50, img_height=90, img_width=120, num_classes=500):
        super(CNN3D, self).__init__()
        self.img_depth = img_depth
        self.img_height = img_height
        self.img_width = img_width
        self.num_classes = num_classes

        # network params
        self.ch1, self.ch2 = 32, 48
        self.k1, self.k2 = (5,5,5), (3,3,3)
        self.s1, self.s2 = (2,2,2), (2,2,2)
        self.p1, self.p2 = (0,0,0), (0,0,0)
        self.d1, self.d2 = (1,1,1), (1,1,1)
        self.hidden1, self.hidden2 = 256, 128
        self.drop_p = 0.2
        self.pool_k = 2
        self.conv1_output_shape = self.compute_output_shape(self.img_depth, self.img_height, 
            self.img_width, self.k1, self.s1, self.p1, self.d1)
        self.conv2_output_shape = self.compute_output_shape(self.conv1_output_shape[0], self.conv1_output_shape[1], 
            self.conv1_output_shape[2], self.k2, self.s2, self.p2, self.d2)
        # print(self.conv1_output_shape, self.conv2_output_shape)

        # network architecture
        # in_channels=1 for grayscale
        self.conv1 = nn.Conv3d(in_channels=1, out_channels=self.ch1, kernel_size=self.k1,
            stride=self.s1, padding=self.p1, dilation=self.d1)
        self.bn1 = nn.BatchNorm3d(self.ch1)
        self.conv2 = nn.Conv3d(in_channels=self.ch1, out_channels=self.ch2, kernel_size=self.k2,
            stride=self.s2, padding=self.p2, dilation=self.d2)
        self.bn2 = nn.BatchNorm3d(self.ch2)
        self.relu = nn.ReLU(inplace=True)
        self.drop = nn.Dropout3d(p=self.drop_p)
        self.pool = nn.MaxPool3d(kernel_size=self.pool_k)
        self.fc1 = nn.Linear(self.ch2 * self.conv2_output_shape[0] * self.conv2_output_shape[1] * self.conv2_output_shape[2], self.hidden1)
        self.fc2 = nn.Linear(self.hidden1, self.hidden2)
        self.fc3 = nn.Linear(self.hidden2, self.num_classes)

    def forward(self, x):
        # Conv1
        x = self.conv1(x)
        x = self.bn1(x)
        x = self.relu(x)
        x = self.drop(x)
        # # Conv2
        x = self.conv2(x)
        x = self.bn2(x)
        x = self.relu(x)
        x = self.drop(x)
        # # MLP
        # print(x.shape)
        # x.size(0) ------ batch_size
        x = x.view(x.size(0), -1)
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = F.dropout(x, p=self.drop_p, training=self.training)
        x = self.fc3(x)

        return x

    def compute_output_shape(self, D_in, H_in, W_in, k, s, p, d):
        D_out = np.floor((D_in + 2*p[0] - d[0]*(k[0] - 1) - 1)/s[0] + 1).astype(int)
        H_out = np.floor((H_in + 2*p[1] - d[1]*(k[1] - 1) - 1)/s[1] + 1).astype(int)
        W_out = np.floor((W_in + 2*p[2] - d[2]*(k[2] - 1) - 1)/s[2] + 1).astype(int)

        return D_out, H_out, W_out

# Test
if __name__ == '__main__':
    import torchvision.transforms as transforms
    from dataset import CSL_Dataset
    transform = transforms.Compose([transforms.Resize([90, 120]), transforms.ToTensor()])
    dataset = CSL_Dataset(data_path="/media/zjunlict/TOSHIBA1/dataset/SLR_dataset/S500_color_video", 
        label_path='/media/zjunlict/TOSHIBA1/dataset/SLR_dataset/dictionary.txt', transform=transform)
    cnn3d = CNN3D()
    print(cnn3d(dataset[0]['images'].unsqueeze(0).unsqueeze(0)))