import torch.nn as nn
from Advanced.Resnet.BasicBlock import BasicBlock
from Advanced.Resnet.Bottleneck import Bottleneck
from Advanced.Resnet.Utils import conv1x1


class ResNet(nn.Module):
    # model = ResNet(Bottleneck, [3, 4, 6, 3], **kwargs) #resnet 50
    def __init__(self, input_channel ,block, layers, num_classes=10, zero_init_residual=True):
        super(ResNet, self).__init__()

        self.inplanes = 64

        self.inputLayer = nn.Sequential(nn.Conv2d(input_channel, 64, kernel_size=7, stride=2, padding=3, bias=False),
                                       nn.BatchNorm2d(64),
                                       nn.ReLU(inplace=True),
                                       nn.MaxPool2d(kernel_size=3, stride=2, padding=1))

        self.inputLayer2 = nn.Sequential(self._make_layer(block, 64, layers[0]),
                                         self._make_layer(block, 128, layers[1], stride=2),
                                         self._make_layer(block, 256, layers[2], stride=2),
                                         self._make_layer(block, 512, layers[3], stride=2))


        self.avgpool = nn.AdaptiveAvgPool2d((1, 1))
        self.fc = nn.Linear(512 * block.expansion, num_classes)

        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                nn.init.kaiming_normal_(m.weight, mode='fan_out', nonlinearity='relu')
            elif isinstance(m, nn.BatchNorm2d):
                nn.init.constant_(m.weight, 1)
                nn.init.constant_(m.bias, 0)

        # Zero-initialize the last BN in each residual branch,
        # so that the residual branch starts with zeros, and each residual block behaves like an identity.
        # This improves the model by 0.2~0.3% according to https://arxiv.org/abs/1706.02677
        if zero_init_residual:
            for m in self.modules():
                if isinstance(m, Bottleneck):
                    nn.init.constant_(m.bn3.weight, 0)
                elif isinstance(m, BasicBlock):
                    nn.init.constant_(m.bn2.weight, 0)

    def _make_layer(self, block, planes, blocks, stride=1):

        downsample = None

        if stride != 1 or self.inplanes != planes * block.expansion:
            downsample = nn.Sequential(
                conv1x1(self.inplanes, planes * block.expansion, stride),  # conv1x1(256, 512, 2)
                nn.BatchNorm2d(planes * block.expansion),  # batchnrom2d(512)
            )

        layers = []
        layers.append(block(self.inplanes, planes, stride, downsample))

        self.inplanes = planes * block.expansion  # self.inplanes = 128 * 4

        for _ in range(1, blocks):
            layers.append(block(self.inplanes, planes))  # * 3

        return nn.Sequential(*layers)

    def forward(self, x):
        x = self.inputLayer(x)
        x = self.inputLayer2(x)
        x = self.avgpool(x)

        x = x.view(x.size(0), -1)
        x = self.fc(x)

        return x


def resnet18(input_Channel, **kwargs):
    model = ResNet(input_Channel, BasicBlock, [2, 2, 2, 2], **kwargs) #=> 2*(2+2+2+2) +1(conv1) +1(fc)  = 16 +2 =resnet 18
    return model


def resnet50(input_Channel, **kwargs):
    model = ResNet(input_Channel, Bottleneck, [3, 4, 6, 3], **kwargs) #=> 3*(3+4+6+3) +(conv1) +1(fc) = 48 +2 = 50
    return model


def resnet152(input_Channel, **kwargs):
    model = ResNet(input_Channel, Bottleneck, [3, 8, 36, 3], **kwargs) # 3*(3+8+36+3) +2 = 150+2 = resnet152
    return model