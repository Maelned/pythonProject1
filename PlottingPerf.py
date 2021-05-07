import numpy as np
import matplotlib.pyplot as plt
import pickle
import itertools
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from operator import truediv, add



Dataset = "E:\\NTNU\\TTM4905 Communication Technology, Master's Thesis\\Code\\Dataset\\"
Test_dir = Dataset + "ISIC2018V2\\Test\\"

model = load_model("Saves/Models/InceptionV3.h5")

test_datagen = ImageDataGenerator(
    rescale=1. / 255.,
    featurewise_center=False,  # set input mean to 0 over the dataset
    samplewise_center=False,  # set each sample mean to 0
    featurewise_std_normalization=False,  # divide inputs by std of the dataset
    samplewise_std_normalization=False,  # divide each input by its std
    zca_whitening=False,  # apply ZCA whitening
)

test_ds = test_datagen.flow_from_directory(
    Test_dir,
    target_size=(224, 224),
    color_mode="rgb",
    classes=None,
    class_mode="categorical",
    batch_size=1,
    shuffle=False,
    seed=False,
    interpolation="bilinear",
    follow_links=False)




def plot_curves(history):

    loss_train = history['loss']
    loss_val = history['val_loss']
    acc_train = history['categorical_accuracy']
    acc_val = history['val_categorical_accuracy']
    values = [[loss_train, loss_val], [acc_train, acc_val]]
    epochs = range(len(loss_train))

    for i in range(2):
        for j in range(2):
            if j :
                plt.plot(epochs, values[i][j] , color = 'b', label = "Validation")
            else:
                plt.plot(epochs, values[i][j] , color = 'g', label = "Training")
            plt.xlabel('Epochs')
            plt.ylabel('Loss')
            plt.legend()
        plt.show()

    # plt.plot(epochs, acc_train, 'g', label='Training acc')
    # plt.plot(epochs, acc_val, 'b', label='validation accuracy')
    # plt.xlabel('Epochs')
    # plt.ylabel('accuracy')
    # plt.legend()
    # plt.show()


def plot_graph(multiple_cm):
    experiment = [5,10,15,20,30,45,60]
    precision_tot,recall_tot,F1_tot,Specificity_tot,Accuracy_tot = [],[],[],[],[]
    for i in multiple_cm:
        plot_metrics(i,"No title",False,False,True)
        macro_avg_precision, macro_avg_recall, macro_avg_F1, Specificity, Accuracy = model_evaluation(i)
        precision_tot.append(macro_avg_precision)
        recall_tot.append( macro_avg_recall)
        F1_tot.append(macro_avg_F1)
        Specificity_tot.append(Specificity)
        Accuracy_tot.append(Accuracy)
    plt.plot(experiment,precision_tot,label = "precision")
    plt.plot(experiment, recall_tot, label="recall")
    plt.plot(experiment, F1_tot, label="F1-score")
    plt.plot(experiment, Specificity_tot, label="Specificity")
    plt.plot(experiment, Accuracy_tot, label="Accuracy")
    plt.xlabel("Different experiement")
    plt.ylabel("Percentage")
    plt.legend()
    plt.show()

def plot_metrics(cm,title,plot_cm,verbose,Attack):
    if plot_cm:
        plot_confusion_matrix(cm,cm_plot_labels,title)
    macro_avg_precision, macro_avg_recall, macro_avg_F1, Specificity, Accuracy = model_evaluation(cm)
    if verbose:
        print("Title : ", title)
        print("Accuracy :", Accuracy)
        print("Macro average recall : ", macro_avg_recall)
        print("Specificity : ", Specificity)
        print("Macro average precision : ", macro_avg_precision)
        print("Macro average F1 : ", macro_avg_F1)
        print("\n")
    if Attack:
        Fooling_rate = 1 - Accuracy
        print("Fooling rate : ",Fooling_rate)


def true_negative(confusion_matrix):
    TN = []
    for label in range(len(confusion_matrix)):
        row = confusion_matrix[label, :]
        col = confusion_matrix[:, label]
        FN = row.sum()
        FP = col.sum()
        TN.append(confusion_matrix.sum() - FN - FP + confusion_matrix[label, label])
    return TN


def true_positive(confusion_matrix):
    TP = []
    for label in range(len(confusion_matrix)):
        TP.append(confusion_matrix[label, label])
    return TP


def false_negative(confusion_matrix):
    FN = []
    for label in range(len(confusion_matrix)):
        FN.append(confusion_matrix[label, :].sum() - confusion_matrix[label, label])
    return FN


def false_positive(confusion_matrix):
    FP = []
    for label in range(len(confusion_matrix)):
        FP.append(confusion_matrix[:, label].sum() - confusion_matrix[label, label])
    return FP

def model_evaluation(confusion_matrix):
    FP = false_positive(confusion_matrix)
    FN = false_negative(confusion_matrix)
    TP = true_positive(confusion_matrix)
    TN = true_negative(confusion_matrix)

    TotalFP = sum(FP)
    TotalFN = sum(FN)
    TotalTP = sum(TP)
    TotalTN = sum(TN)

    specificity_list = list(map(truediv, TN, list(map(add, TN, FP))))

    Precision_list = list(map(truediv, TP, list(map(add, TP, FP))))

    Recall_list = list(map(truediv, TP, list(map(add, TP, FN))))

    specificity_avg = np.around(sum(specificity_list) / len(specificity_list), 4)

    macro_avg_precision = np.around(sum(Precision_list) / len(Precision_list), 4)

    macro_avg_recall = np.around(sum(Recall_list) / len(Recall_list),4)

    macro_avg_F1 = np.around(2 * ((macro_avg_precision * macro_avg_precision) / (macro_avg_precision + macro_avg_recall)),4)

    Accuracy = np.around(confusion_matrix.trace() / confusion_matrix.sum(), 4)

    return macro_avg_precision, macro_avg_recall, macro_avg_F1, specificity_avg, Accuracy


def plot_confusion_matrix(cm, classes,
                          normalize=True,
                          title='Confusion matrix',
                          cmap=plt.cm.Blues):
    """
    This function prints and plots the confusion matrix.
    Normalization can be applied by setting `normalize=True`.
    """
    # plt.title(title)
    # plt.colorbar()
    plt.figure(figsize=(5, 5))
    tick_marks = np.arange(len(classes))
    plt.xticks(tick_marks, classes)
    plt.yticks(tick_marks, classes)
    if normalize:
        cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis] * 100
        cm = np.around(cm, 1)
        # print("Normalized confusion matrix")
    else:
        print('Confusion matrix, without normalization')
    thresh = cm.max() / 2.
    for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
        plt.text(j, i, cm[i, j],
                 horizontalalignment="center",
                 color="white" if cm[i, j] > thresh else "black")
    plt.imshow(cm, interpolation='nearest', cmap=cmap)

    plt.ylabel('True label')
    plt.xlabel('Predicted label')
    plt.tight_layout()
    plt.show()


history = np.load('Saves/Hitsory/history_InceptionV3.npy', allow_pickle='TRUE').item()


with open("./Saves/ConfusionMatrixes/ConfusionMatrix_inceptionV3_AttackedModel_05nv-bkl_3.pkl", "rb") as f:
    cm_attacked5 = pickle.load(f)

with open("./Saves/ConfusionMatrixes/ConfusionMatrix_InceptionV3_AttackedModel_10nv-bkl_3.pkl", "rb") as f:
    cm_attacked10 = pickle.load(f)

with open("./Saves/ConfusionMatrixes/ConfusionMatrix_InceptionV3_AttackedModel_15nv-bkl_3.pkl", "rb") as f:
    cm_attacked15 = pickle.load(f)

with open("./Saves/ConfusionMatrixes/ConfusionMatrix_InceptionV3_AttackedModel_20nv-bkl_3.pkl", "rb") as f:
    cm_attacked20 = pickle.load(f)

with open("./Saves/ConfusionMatrixes/ConfusionMatrix_InceptionV3_AttackedModel_30nv-bkl_3.pkl", "rb") as f:
    cm_attacked30 = pickle.load(f)

with open("./Saves/ConfusionMatrixes/ConfusionMatrix_InceptionV3_AttackedModel_45nv-bkl_3.pkl", "rb") as f:
    cm_attacked45 = pickle.load(f)

with open("./Saves/ConfusionMatrixes/ConfusionMatrix_InceptionV3_AttackedModel_60nv-bkl_3.pkl", "rb") as f:
    cm_attacked60 = pickle.load(f)

with open("./Saves/ConfusionMatrixes/ConfusionMatrix_AfterFGSM_InceptionV3_0.pkl", "rb") as f:
    cm_FGSM_0 = pickle.load(f)

with open("./Saves/ConfusionMatrixes/ConfusionMatrix_AfterFGSM_InceptionV3_0.00784313725490196.pkl", "rb") as f:
    cm_FGSM_0007 = pickle.load(f)

with open("./Saves/ConfusionMatrixes/ConfusionMatrix_AfterFGSM_InceptionV3_0.01.pkl", "rb") as f:
    cm_FGSM_001 = pickle.load(f)

with open("./Saves/ConfusionMatrixes/ConfusionMatrix_AfterFGSM_InceptionV3_0.1.pkl", "rb") as f:
    cm_FGSM_01 = pickle.load(f)

with open("./Saves/ConfusionMatrixes/ConfusionMatrix_AfterFGSM_InceptionV3_0.15.pkl", "rb") as f:
    cm_FGSM_015 = pickle.load(f)

with open("./Saves/ConfusionMatrixes/ConfusionMatrix_BeforeFGSM_InceptionV3_.pkl", "rb") as f:
    cm_Before_FGSM = pickle.load(f)

with open("./Saves/ConfusionMatrixes/ConfusionMatrix_NonTargetedUAP_InceptionV3.pkl", "rb") as f:
    cm_UAP = pickle.load(f)

cm_plot_labels = ['akiec', 'bcc', 'bkl', 'df', 'mel', 'nv', 'vasc']


plot_curves(history)
# Y_pred = model.predict_generator(test_ds, steps = test_ds.samples)
# y_pred = np.argmax(Y_pred, axis=1)


# cm_inception = confusion_matrix(test_ds.classes,y_pred)


multi_cm = [cm_attacked5,cm_attacked10,cm_attacked15,cm_attacked20,cm_attacked30,cm_attacked45,cm_attacked60]
plot_graph(multi_cm)

# plot_metrics(cm_inception,"Inception V3",True,True,False)

plot_metrics(cm_Before_FGSM,"Inception Before V3 FGSM",True,True,False)
# plot_metrics(cm_FGSM_0,"Inception V3 FGSM epsilon 0",True,True,True)
# plot_metrics(cm_FGSM_0007,"Inception V3 FGSM epsilon 0.007",True,True,True)
# plot_metrics(cm_FGSM_001,"Inception V3 FGSM epsilon 0.01",True,True,True)
# plot_metrics(cm_FGSM_01,"Inception V3 FGSM epsilon 0.1",True,True,True)
# plot_metrics(cm_FGSM_015,"Inception V3 FGSM epsilon 0.15",True,True,True)
plot_metrics(cm_UAP,"Inception V3 Non targeted UAP", True,True,True)
# plot_metrics(cm_attacked5,"Inception V3 Attacked 5%",True,True)
# plot_metrics(cm_attacked10,"Inception V3 Attacked 10%",True,True)
# plot_metrics(cm_attacked15,"Inception V3 Attacked 15%",True,True)
# plot_metrics(cm_attacked20,"Inception V3 Attacked 20%",True,True)
# plot_metrics(cm_attacked30,"Inception V3 Attacked 30%")
# plot_metrics(cm_attacked45,"Inception V3 Attacked 45%")
# plot_metrics(cm_attacked60,"Inception V3 Attacked 60%")
# plot_metrics(cm_attacked75,"Inception V3 Attacked 75%")
