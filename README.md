# DLS-telegram-bot

style_model.py - реализация своего GAN для переноса стилей

Реализация алгоритма переноса стиля, предложенного Леоном Гатисом в 2015 году, с помощью Keras и Tensorflow.

В основе была звята модель VGG19.

![image](https://user-images.githubusercontent.com/10894752/177983809-5b9089bb-1209-417a-84d1-74acefb37e03.png)



style_transfer_bot.py - реализация асинхронного телеграм-бота

Для реализации была взята готовая модель из tensorflow hub (https://tfhub.dev/google/magenta/arbitrary-image-stylization-v1-256/2) 

Модель была разработана основываясь на модели из magenta (https://github.com/magenta/magenta/tree/main/magenta/models/arbitrary_image_stylization)

и публикации:
Exploring the structure of a real-time, arbitrary neural artistic stylization network. Golnaz Ghiasi, Honglak Lee, Manjunath Kudlur, Vincent Dumoulin, Jonathon Shlens, Proceedings of the British Machine Vision Conference (BMVC), 2017.

