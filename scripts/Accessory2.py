"""
Calculation of metrics including accuracy, AUROC, and PRC, outputing CAM of tiles, and output
last layer activation for tSNE 2.0

Created on 04/26/2019

@author: RH
"""
import matplotlib
matplotlib.use('Agg')
import os
import numpy as np
import sklearn.metrics
from scipy import interp
import matplotlib.pyplot as plt
import pandas as pd
import cv2
from itertools import cycle


# Plot ROC and PRC plots
def ROC_PRC(outtl, pdx, path, name, fdict, dm, accur, pmd):
    if pmd == 'stage' or pmd == 'grade':
        rdd = 5
    elif pmd == 'origin':
        rdd = 10
    elif pmd == 'cellularity' or pmd == 'nuclei' or pmd == 'necrosis':
        rdd = 3
    else:
        rdd = 2
    if rdd > 2:
        # Compute ROC and PRC curve and ROC and PRC area for each class
        fpr = dict()
        tpr = dict()
        roc_auc = dict()
        # PRC
        # For each class
        precision = dict()
        recall = dict()
        average_precision = dict()
        microy = []
        microscore = []
        for i in range(rdd):
            fpr[i], tpr[i], _ = sklearn.metrics.roc_curve(np.asarray((outtl.iloc[:, 0].values == int(i)).astype('uint8')),
                                                      np.asarray(pdx[:, i]).ravel())
            try:
                roc_auc[i] = sklearn.metrics.roc_auc_score(np.asarray((outtl.iloc[:, 0].values == int(i)).astype('uint8')),
                                                       np.asarray(pdx[:, i]).ravel())
            except ValueError:
                roc_auc[i] = np.nan

            microy.extend(np.asarray((outtl.iloc[:, 0].values == int(i)).astype('uint8')))
            microscore.extend(np.asarray(pdx[:, i]).ravel())

            precision[i], recall[i], _ = \
                sklearn.metrics.precision_recall_curve(np.asarray((outtl.iloc[:, 0].values == int(i)).astype('uint8')),
                                                   np.asarray(pdx[:, i]).ravel())
            try:
                average_precision[i] = \
                    sklearn.metrics.average_precision_score(np.asarray((outtl.iloc[:, 0].values == int(i)).astype('uint8')),
                                                        np.asarray(pdx[:, i]).ravel())
            except ValueError:
                average_precision[i] = np.nan

        # Compute micro-average ROC curve and ROC area
        fpr["micro"], tpr["micro"], _ = sklearn.metrics.roc_curve(np.asarray(microy).ravel(),
                                                              np.asarray(microscore).ravel())
        roc_auc["micro"] = sklearn.metrics.auc(fpr["micro"], tpr["micro"])

        # A "micro-average": quantifying score on all classes jointly
        precision["micro"], recall["micro"], _ = sklearn.metrics.precision_recall_curve(np.asarray(microy).ravel(),
                                                                                    np.asarray(microscore).ravel())
        average_precision["micro"] = sklearn.metrics.average_precision_score(np.asarray(microy).ravel(),
                                                                         np.asarray(microscore).ravel(),
                                                                         average="micro")

        # Compute macro-average ROC curve and ROC area

        # First aggregate all false positive rates
        all_fpr = np.unique(np.concatenate([fpr[i] for i in range(rdd)]))

        # Then interpolate all ROC curves at this points
        mean_tpr = np.zeros_like(all_fpr)
        for i in range(rdd):
            mean_tpr += interp(all_fpr, fpr[i], tpr[i])

        # Finally average it and compute AUC
        mean_tpr /= rdd

        fpr["macro"] = all_fpr
        tpr["macro"] = mean_tpr
        roc_auc["macro"] = sklearn.metrics.auc(fpr["macro"], tpr["macro"])

        # Plot all ROC curves
        plt.figure()
        plt.plot(fpr["micro"], tpr["micro"],
                 label='micro-average ROC curve (area = {0:0.5f})'
                       ''.format(roc_auc["micro"]),
                 color='deeppink', linestyle=':', linewidth=4)

        plt.plot(fpr["macro"], tpr["macro"],
                 label='macro-average ROC curve (area = {0:0.5f})'
                       ''.format(roc_auc["macro"]),
                 color='navy', linestyle=':', linewidth=4)

        colors = cycle(['aqua', 'darkorange', 'cornflowerblue', 'red', 'blue'])
        for i, color in zip(range(rdd), colors):
            plt.plot(fpr[i], tpr[i], color=color, lw=2,
                     label='ROC curve of {0} (area = {1:0.5f})'.format(fdict[i], roc_auc[i]))
            print('{0} {1} AUC of {2} = {3:0.5f}'.format(name, dm, fdict[i], roc_auc[i]))

        plt.plot([0, 1], [0, 1], 'k--', lw=2)
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title('ROC of {}'.format(name))
        plt.legend(loc="lower right")
        plt.savefig("../Results/{}/out/{}_{}_ROC.png".format(path, name, dm))

        print('{0} Average precision score, micro-averaged over all classes: {1:0.5f}'.format(name, average_precision["micro"]))
        # Plot all PRC curves
        colors = cycle(['navy', 'turquoise', 'darkorange', 'cornflowerblue', 'teal', 'red', 'blue'])
        plt.figure(figsize=(7, 9))
        f_scores = np.linspace(0.2, 0.8, num=4)
        lines = []
        labels = []
        for f_score in f_scores:
            x = np.linspace(0.01, 1)
            y = f_score * x / (2 * x - f_score)
            l, = plt.plot(x[y >= 0], y[y >= 0], color='gray', alpha=0.2)
            plt.annotate('f1={0:0.1f}'.format(f_score), xy=(0.9, y[45] + 0.02))
        lines.append(l)
        labels.append('iso-f1 curves')

        l, = plt.plot(recall["micro"], precision["micro"], color='gold', lw=2)
        lines.append(l)
        labels.append('micro-average Precision-recall (area = {0:0.5f})'
                      ''.format(average_precision["micro"]))

        for i, color in zip(range(rdd), colors):
            l, = plt.plot(recall[i], precision[i], color=color, lw=2)
            lines.append(l)
            labels.append('Precision-recall for {0} (area = {1:0.5f})'.format(fdict[i], average_precision[i]))
            print('{0} {1} Average Precision of {2} = {3:0.5f}'.format(name, dm, fdict[i], average_precision[i]))

        fig = plt.gcf()
        fig.subplots_adjust(bottom=0.25)
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel('Recall')
        plt.ylabel('Precision')
        plt.title('{} Precision-Recall curve: Average Accu={}'.format(name, accur))
        plt.legend(lines, labels, loc=(0, -.38), prop=dict(size=12))
        plt.savefig("../Results/{}/out/{}_{}_PRC.png".format(path, name, dm))

    else:
        tl = outtl.values[:, 0].ravel()
        y_score = np.asarray(pdx[:, 1]).ravel()
        auc = sklearn.metrics.roc_auc_score(tl, y_score)
        auc = round(auc, 5)
        print('{0} {1} AUC = {2:0.5f}'.format(name, dm, auc))
        fpr, tpr, _ = sklearn.metrics.roc_curve(tl, y_score)
        plt.figure()
        lw = 2
        plt.plot(fpr, tpr, color='darkorange',
                 lw=lw, label='ROC curve (area = %0.5f)' % auc)
        plt.plot([0, 1], [0, 1], color='navy', lw=lw, linestyle='--')
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title('{} ROC of {}'.format(name, pmd))
        plt.legend(loc="lower right")
        plt.savefig("../Results/{}/out/{}_{}_ROC.png".format(path, name, dm))

        average_precision = sklearn.metrics.average_precision_score(tl, y_score)
        print('{0} Average precision-recall score: {1:0.5f}'.format(name, average_precision))
        plt.figure()
        f_scores = np.linspace(0.2, 0.8, num=4)
        for f_score in f_scores:
            x = np.linspace(0.01, 1)
            y = f_score * x / (2 * x - f_score)
            l, = plt.plot(x[y >= 0], y[y >= 0], color='gray', alpha=0.2)
            plt.annotate('f1={0:0.1f}'.format(f_score), xy=(0.9, y[45] + 0.02))
        precision, recall, _ = sklearn.metrics.precision_recall_curve(tl, y_score)
        plt.step(recall, precision, color='b', alpha=0.2,
                 where='post')
        plt.fill_between(recall, precision, step='post', alpha=0.2,
                         color='b')
        plt.xlabel('Recall')
        plt.ylabel('Precision')
        plt.ylim([0.0, 1.05])
        plt.xlim([0.0, 1.0])
        plt.title('{} {} PRC: AP={:0.5f}; Accu={}'.format(pmd, name, average_precision, accur))
        plt.savefig("../Results/{}/out/{}_{}_PRC.png".format(path, name, dm))


# slide level; need prediction scores, true labels, output path, and name of the files for metrics;
# accuracy, AUROC; AUPRC.
def slide_metrics(inter_pd, path, name, fordict, pmd):
    inter_pd = inter_pd.drop(['Patient_ID', 'Tumor', 'L1path', 'L2path', 'L3path', 'label', 'Prediction'], axis=1)
    inter_pd = inter_pd.groupby(['Slide_ID']).mean()    # Need to change in transfer learning
    inter_pd = inter_pd.round({'True_label': 0})
    if pmd == 'stage':
        inter_pd['Prediction'] = inter_pd[
            ['stage0_score', 'stage1_score', 'stage2_score', 'stage3_score', 'stage4_score']].idxmax(axis=1)
        redict = {'stage1_score': int(1), 'stage2_score': int(2), 'stage3_score': int(3), 'stage4_score': int(4),
                  'stage0_score': int(0)}
    elif pmd == "grade":
        inter_pd['Prediction'] = inter_pd[
            ['grade0_score', 'grade1_score', 'grade2_score', 'grade3_score', 'grade4_score']].idxmax(axis=1)
        redict = {'grade1_score': int(1), 'grade2_score': int(2), 'grade3_score': int(3), 'grade4_score': int(4),
                  'grade0_score': int(0)}
    elif pmd == "cellularity":
        inter_pd['Prediction'] = inter_pd[
            ['0_79_score', '80_89_score', '90_100_score']].idxmax(axis=1)
        redict = {'0_79_score': int(0), '80_89_score': int(1), '90_100_score': int(2)}
    elif pmd == "nuclei":
        inter_pd['Prediction'] = inter_pd[
            ['0_49_score', '50_79_score', '80_100_score']].idxmax(axis=1)
        redict = {'0_49_score': int(0), '50_79_score': int(1), '80_100_score': int(2)}
    elif pmd == "necrosis":
        inter_pd['Prediction'] = inter_pd[
            ['0_score', '1_9_score', '10_100_score']].idxmax(axis=1)
        redict = {'0_score': int(0), '1_9_score': int(1), '10_100_score': int(2)}
    elif pmd == 'origin':
        inter_pd['Prediction'] = inter_pd[['HNSCC_score', 'CCRCC_score', 'CO_score', 'BRCA_score', 'LUAD_score',
                                           'LSCC_score', 'PDA_score', 'UCEC_score', 'GBM_score',
                                           'OV_score']].idxmax(axis=1)
        redict = {'HNSCC_score': int(0), 'CCRCC_score': int(1), 'CO_score': int(2), 'BRCA_score': int(3),
                  'LUAD_score': int(4), 'LSCC_score': int(5), 'PDA_score': int(6), 'UCEC_score': int(7),
                  'GBM_score': int(8), 'OV_score': int(9)}
    else:
        inter_pd['Prediction'] = inter_pd[['NEG_score', 'POS_score']].idxmax(axis=1)
        redict = {'NEG_score': int(0), 'POS_score': int(1)}
    inter_pd['Prediction'] = inter_pd['Prediction'].replace(redict)

    # accuracy calculations
    tott = inter_pd.shape[0]
    accout = inter_pd.loc[inter_pd['Prediction'] == inter_pd['True_label']]
    accu = accout.shape[0]
    accurr = round(accu/tott, 5)
    print('Slide Total Accuracy: '+str(accurr))
    if pmd == 'stage' or pmd == 'grade':
        for i in range(5):
            accua = accout[accout.True_label == i].shape[0]
            tota = inter_pd[inter_pd.True_label == i].shape[0]
            try:
                accuar = round(accua / tota, 5)
                print('Slide {} Accuracy: '.format(fordict[i])+str(accuar))
            except ZeroDivisionError:
                print("No data for {}.".format(fordict[i]))
    elif pmd == 'origin':
        for i in range(10):
            accua = accout[accout.True_label == i].shape[0]
            tota = inter_pd[inter_pd.True_label == i].shape[0]
            try:
                accuar = round(accua / tota, 5)
                print('Slide {} Accuracy: '.format(fordict[i])+str(accuar))
            except ZeroDivisionError:
                print("No data for {}.".format(fordict[i]))
    elif pmd == 'cellularity' or pmd == 'nuclei' or pmd == 'necrosis':
        for i in range(3):
            accua = accout[accout.True_label == i].shape[0]
            tota = inter_pd[inter_pd.True_label == i].shape[0]
            try:
                accuar = round(accua / tota, 5)
                print('Slide {} Accuracy: '.format(fordict[i])+str(accuar))
            except ZeroDivisionError:
                print("No data for {}.".format(fordict[i]))
    try:
        outtl_slide = inter_pd['True_label'].to_frame(name='True_lable')
        if pmd == 'stage':
            pdx_slide = inter_pd[
                ['stage0_score', 'stage1_score', 'stage2_score', 'stage3_score', 'stage4_score']].values
        elif pmd == "grade":
            pdx_slide = inter_pd[
                ['grade0_score', 'grade1_score', 'grade2_score', 'grade3_score', 'grade4_score']].values
        elif pmd == "cellularity":
            pdx_slide = inter_pd[
                ['0_79_score', '80_89_score', '90_100_score']].values
        elif pmd == "nuclei":
            pdx_slide = inter_pd[
                ['0_49_score', '50_79_score', '80_100_score']].values
        elif pmd == "necrosis":
            pdx_slide = inter_pd[
                ['0_score', '1_9_score', '10_100_score']].values
        elif pmd == 'origin':
            pdx_slide = inter_pd[['HNSCC_score', 'CCRCC_score', 'CO_score', 'BRCA_score', 'LUAD_score',
                                           'LSCC_score', 'PDA_score', 'UCEC_score', 'GBM_score',
                                           'OV_score']].values
        else:
            pdx_slide = inter_pd[['NEG_score', 'POS_score']].values
        ROC_PRC(outtl_slide, pdx_slide, path, name, fordict, 'slide', accurr, pmd)
    except ValueError:
        print('Not able to generate plots based on this set!')
    inter_pd['Prediction'] = inter_pd['Prediction'].replace(fordict)
    inter_pd['True_label'] = inter_pd['True_label'].replace(fordict)

    raw = pd.read_csv("../Results/{}/data/{}_sample_raw.csv".format(path, name[0:2].lower()),
                      header=0, usecols=['Slide_ID', 'Tumor', 'Patient_ID', 'path'])
    inter_pd = inter_pd.join(raw.set_index('Slide_ID'), on='Slide_ID', how='left')
    inter_pd.to_csv("../Results/{}/out/{}_slide.csv".format(path, name), index=True)


# for real image prediction, just output the prediction scores as csv
def realout(pdx, path, name, pmd):
    if pmd == 'stage':
        lbdict = {1: 'stage1', 2: 'stage2', 3: 'stage3', 4: 'stage4', 0: 'stage0'}
    elif pmd == "grade":
        lbdict = {1: 'grade1', 2: 'grade2', 3: 'grade3', 4: 'grade4', 0: 'grade0'}
    elif pmd == "cellularity":
        lbdict = {0: '0_79', 1: '80_89', 2: '90_100'}
    elif pmd == "nuclei":
        lbdict = {0: '0_49', 1: '50_79', 2: '80_100'}
    elif pmd == "necrosis":
        lbdict = {0: '0', 1: '1_9', 2: '10_100'}
    elif pmd == 'origin':
        lbdict = {0: 'HNSCC', 1: 'CCRCC', 2: 'CO', 3: 'BRCA', 4: 'LUAD',
                  5: 'LSCC', 6: 'PDA', 7: 'UCEC', 8: 'GBM', 9: 'OV'}
    else:
        lbdict = {0: 'negative', 1: pmd}
    pdx = np.asmatrix(pdx)
    prl = pdx[:, 0:20].argmax(axis=1).astype('uint8')
    prl = pd.DataFrame(prl, columns=['Prediction'])
    prl = prl.replace(lbdict)
    if pmd == 'stage':
        pdx = np.concatenate((pdx[:, 0:5], pdx[:, 20:]), axis=1)
        out = pd.DataFrame(pdx,
                           columns=['stage0_score', 'stage1_score', 'stage2_score', 'stage3_score', 'stage4_score',
                                    'oll1path', 'hml1path', 'oll2path', 'hml2path', 'oll3path', 'hml3path'])
    elif pmd == 'grade':
        pdx = np.concatenate((pdx[:, 0:5], pdx[:, 20:]), axis=1)
        out = pd.DataFrame(pdx,
                           columns=['grade0_score', 'grade1_score', 'grade2_score', 'grade3_score', 'grade4_score',
                                    'oll1path', 'hml1path', 'oll2path', 'hml2path', 'oll3path', 'hml3path'])
    elif pmd == 'cellularity':
        pdx = np.concatenate((pdx[:, 0:3], pdx[:, 20:]), axis=1)
        out = pd.DataFrame(pdx,
                           columns=['0_79_score', '80_89_score', '90_100_score',
                                    'oll1path', 'hml1path', 'oll2path', 'hml2path', 'oll3path', 'hml3path'])
    elif pmd == 'nuclei':
        pdx = np.concatenate((pdx[:, 0:3], pdx[:, 20:]), axis=1)
        out = pd.DataFrame(pdx,
                           columns=['0_49_score', '50_79_score', '80_100_score',
                                    'oll1path', 'hml1path', 'oll2path', 'hml2path', 'oll3path', 'hml3path'])
    elif pmd == 'necrosis':
        pdx = np.concatenate((pdx[:, 0:3], pdx[:, 20:]), axis=1)
        out = pd.DataFrame(pdx,
                           columns=['0_score', '1_9_score', '10_100_score',
                                    'oll1path', 'hml1path', 'oll2path', 'hml2path', 'oll3path', 'hml3path'])
    elif pmd == 'origin':
        pdx = np.concatenate((pdx[:, 0:10], pdx[:, 20:]), axis=1)
        out = pd.DataFrame(pdx,
                           columns=['HNSCC_score', 'CCRCC_score', 'CO_score', 'BRCA_score', 'LUAD_score', 'LSCC_score',
                                    'PDA_score', 'UCEC_score', 'GBM_score', 'OV_score',
                                    'oll1path', 'hml1path', 'oll2path', 'hml2path', 'oll3path', 'hml3path'])
    else:
        pdx = np.concatenate((pdx[:, 0:2], pdx[:, 20:]), axis=1)
        out = pd.DataFrame(pdx, columns=['NEG_score', 'POS_score',
                                                 'oll1path', 'hml1path', 'oll2path',
                                                 'hml2path', 'oll3path', 'hml3path'])
    out.reset_index(drop=True, inplace=True)
    prl.reset_index(drop=True, inplace=True)
    out = pd.concat([out, prl], axis=1)
    out.insert(loc=0, column='Num', value=out.index)
    out.to_csv("{}/{}.csv".format(path, name), index=False)


def type_metrics(path, name, pmd, fdict):
    if name == 'Validation':
        pass
    else:
        bdict = {value: key for (key, value) in fdict.items()}
        slide = pd.read_csv("../Results/{}/out/{}_slide.csv".format(path, name), header=0)
        tile = pd.read_csv("../Results/{}/out/{}_tile.csv".format(path, name), header=0)
        unq = slide.Tumor.unique().tolist()
        for tt in unq:
            slide_sub = slide[slide['Tumor'] == tt]
            tott = slide_sub.shape[0]
            accout = slide_sub.loc[slide_sub['Prediction'] == slide_sub['True_label']]
            accu = accout.shape[0]
            accur = round(accu / tott, 5)
            outtl = slide_sub['True_label'].replace(bdict).to_frame()
            pdx = slide_sub.filter(regex='_score').values
            try:
                ROC_PRC(outtl, pdx, path, str(tt+'_'+name), fdict, 'slide', accur, pmd)
            except ValueError:
                print('Error: {} contains only 1 level of true label'.format(str(tt+'_'+name)))

            tile_sub = tile[tile['Tumor'] == tt]
            tott = tile_sub.shape[0]
            accout = tile_sub.loc[tile_sub['Prediction'] == tile_sub['True_label']]
            accu = accout.shape[0]
            accur = round(accu / tott, 5)
            outtl = tile_sub['True_label'].replace(bdict).to_frame()
            pdx = tile_sub.filter(regex='_score').values
            try:
                ROC_PRC(outtl, pdx, path, str(tt+'_'+name), fdict, 'tile', accur, pmd)
            except ValueError:
                print('Error: {} contains only 1 level of true label'.format(str(tt+'_'+name)))


# tile level; need prediction scores, true labels, output path, and name of the files for metrics; accuracy, AUROC; PRC.
def metrics(pdx, tl, path, name, pmd, ori_test=None):
    # format clean up
    tl = np.asmatrix(tl)
    tl = tl.argmax(axis=1).astype('uint8')
    pdxt = np.asmatrix(pdx)
    prl = pdxt.argmax(axis=1).astype('uint8')
    prl = pd.DataFrame(prl, columns=['Prediction'])
    if pmd == 'stage':
        lbdict = {1: 'stage1', 2: 'stage2', 3: 'stage3', 4: 'stage4', 0: 'stage0'}
        outt = pd.DataFrame(pdxt[:, 0:5],
                            columns=['stage0_score', 'stage1_score', 'stage2_score', 'stage3_score', 'stage4_score'])
    elif pmd == "grade":
        lbdict = {1: 'grade1', 2: 'grade2', 3: 'grade3', 4: 'grade4', 0: 'grade0'}
        outt = pd.DataFrame(pdxt[:, 0:5],
                           columns=['grade0_score', 'grade1_score', 'grade2_score', 'grade3_score', 'grade4_score'])
    elif pmd == "cellularity":
        lbdict = {0: '0_79', 1: '80_89', 2: '90_100'}
        outt = pd.DataFrame(pdxt[:, 0:3],
                           columns=['0_79_score', '80_89_score', '90_100_score'])
    elif pmd == "nuclei":
        lbdict = {0: '0_49', 1: '50_79', 2: '80_100'}
        outt = pd.DataFrame(pdxt[:, 0:3],
                           columns=['0_49_score', '50_79_score', '80_100_score'])
    elif pmd == "necrosis":
        lbdict = {0: '0', 1: '1_9', 2: '10_100'}
        outt = pd.DataFrame(pdxt[:, 0:3],
                           columns=['0_score', '1_9_score', '10_100_score'])
    elif pmd == 'origin':
        lbdict = {0: 'HNSCC', 1: 'CCRCC', 2: 'CO', 3: 'BRCA', 4: 'LUAD',
                  5: 'LSCC', 6: 'PDA', 7: 'UCEC', 8: 'GBM', 9: 'OV'}
        outt = pd.DataFrame(pdxt[:, 0:10],
                           columns=['HNSCC_score', 'CCRCC_score', 'CO_score', 'BRCA_score', 'LUAD_score', 'LSCC_score',
                                    'PDA_score', 'UCEC_score', 'GBM_score', 'OV_score'])
    else:
        lbdict = {0: 'negative', 1: pmd}
        outt = pd.DataFrame(pdxt[:, 0:2], columns=['NEG_score', 'POS_score'])
    outtlt = pd.DataFrame(tl, columns=['True_label'])
    if name == 'Validation' or name == 'Training':
        outtlt = outtlt.round(0)
    outt.reset_index(drop=True, inplace=True)
    prl.reset_index(drop=True, inplace=True)
    outtlt.reset_index(drop=True, inplace=True)
    out = pd.concat([outt, prl, outtlt], axis=1)
    if ori_test is not None:
        ori_test.reset_index(drop=True, inplace=True)
        out.reset_index(drop=True, inplace=True)
        out = pd.concat([ori_test, out], axis=1)
        slide_metrics(out, path, name, lbdict, pmd)

    stprl = prl.replace(lbdict)
    stouttl = outtlt.replace(lbdict)
    outt.reset_index(drop=True, inplace=True)
    stprl.reset_index(drop=True, inplace=True)
    stouttl.reset_index(drop=True, inplace=True)
    stout = pd.concat([outt, stprl, stouttl], axis=1)
    if ori_test is not None:
        ori_test.reset_index(drop=True, inplace=True)
        stout.reset_index(drop=True, inplace=True)
        stout = pd.concat([ori_test, stout], axis=1)
    stout.to_csv("../Results/{}/out/{}_tile.csv".format(path, name), index=False)

    # accuracy calculations
    tott = out.shape[0]
    accout = out.loc[out['Prediction'] == out['True_label']]
    accu = accout.shape[0]
    accurw = round(accu/tott, 5)
    print('Tile Total Accuracy: '+str(accurw))
    if pmd == 'stage' or pmd == 'grade':
        for i in range(5):
            accua = accout[accout.True_label == i].shape[0]
            tota = out[out.True_label == i].shape[0]
            try:
                accuar = round(accua / tota, 5)
                print('Tile {} Accuracy: '.format(lbdict[i])+str(accuar))
            except ZeroDivisionError:
                print("No data for {}.".format(lbdict[i]))
    if pmd == 'cellularity' or pmd == 'nuclei' or pmd == 'necrosis':
        for i in range(3):
            accua = accout[accout.True_label == i].shape[0]
            tota = out[out.True_label == i].shape[0]
            try:
                accuar = round(accua / tota, 5)
                print('Tile {} Accuracy: '.format(lbdict[i])+str(accuar))
            except ZeroDivisionError:
                print("No data for {}.".format(lbdict[i]))
    elif pmd == 'origin':
        for i in range(10):
            accua = accout[accout.True_label == i].shape[0]
            tota = out[out.True_label == i].shape[0]
            try:
                accuar = round(accua / tota, 5)
                print('Tile {} Accuracy: '.format(lbdict[i])+str(accuar))
            except ZeroDivisionError:
                print("No data for {}.".format(lbdict[i]))
    try:
        ROC_PRC(outtlt, pdxt, path, name, lbdict, 'tile', accurw, pmd)
    except ValueError:
        print('Not able to generate plots based on this set!')
    type_metrics(path, name, pmd, lbdict)


# format activation and weight to get heatmap
def py_returnCAMmap(activation, weights_LR):
    n_feat, w, h, n = activation.shape
    act_vec = np.reshape(activation, [n_feat, w*h])
    n_top = weights_LR.shape[0]
    out = np.zeros([w, h, n_top])
    for t in range(n_top):
        weights_vec = np.reshape(weights_LR[t], [1, weights_LR[t].shape[0]])
        heatmap_vec = np.dot(weights_vec, act_vec)
        heatmap = np.reshape(np.squeeze(heatmap_vec), [w, h])
        out[:, :, t] = heatmap
    return out


# image to double
def im2double(im):
    return cv2.normalize(im.astype('float'), None, 0.0, 1.0, cv2.NORM_MINMAX)


# image to jpg
def py_map2jpg(imgmap):
    heatmap_x = np.round(imgmap*255).astype(np.uint8)
    return cv2.applyColorMap(heatmap_x, cv2.COLORMAP_JET)


# generating CAM plots of each tile; net is activation; w is weight; pred is prediction scores; x are input images;
# y are labels; path is output folder, name is test/validation; rd is current batch number
def CAM(net, w, pred, x, y, path, name, bs, pmd, rd=0):
    DIRT = "../Results/{}/out/{}_img".format(path, name)
    try:
        os.mkdir(DIRT)
    except FileExistsError:
        pass
    if pmd == 'stage':
        catdict = {1: 'stage1', 2: 'stage2', 3: 'stage3', 4: 'stage4', 0: 'stage0'}
    elif pmd == 'grade':
        catdict = {1: 'grade1', 2: 'grade2', 3: 'grade3', 4: 'grade4', 0: 'grade0'}
    elif pmd == 'cellularity':
        catdict = {0: '0_79', 1: '80_89', 2: '90_100'}
    elif pmd == 'nuclei':
        catdict = {0: '0_49', 1: '50_79', 2: '80_100'}
    elif pmd == 'necrosis':
        catdict = {0: '0', 1: '1_9', 2: '10_100'}
    elif pmd == 'origin':
        catdict = {0: 'HNSCC', 1: 'CCRCC', 2: 'CO', 3: 'BRCA', 4: 'LUAD',
                  5: 'LSCC', 6: 'PDA', 7: 'UCEC', 8: 'GBM', 9: 'OV'}
    else:
        catdict = {0: 'negative', 1: pmd}

    y = np.asmatrix(y)
    y = y.argmax(axis=1).astype('uint8')
    rd = rd*bs
    pdx = np.asmatrix(pred)

    prl = pdx.argmax(axis=1).astype('uint8')

    for ij in range(len(y)):
        id = str(ij + rd)
        if prl[ij, 0] == y[ij]:
            ddt = 'Correct'
        else:
            ddt = 'Wrong'

        weights_LR = w

        activation_lastconv = np.array([net[ij]])
        weights_LR = weights_LR.T
        activation_lastconv = activation_lastconv.T

        topNum = 1  # generate heatmap for top X prediction results
        prdd = prl[ij, 0]
        curCAMmapAll = py_returnCAMmap(activation_lastconv, weights_LR[[prdd], :])
        catt = catdict[prdd]
        for kk in range(topNum):
            curCAMmap_crops = curCAMmapAll[:, :, kk]
            curCAMmapLarge_crops = cv2.resize(curCAMmap_crops, (299, 299))
            ### Added Relu ###
            curCAMmapLarge_crops = np.clip(curCAMmapLarge_crops, 0, np.max(curCAMmapLarge_crops))
            ### Added Relu ###
            curHeatMap = cv2.resize(im2double(curCAMmapLarge_crops), (299, 299))
            curHeatMap = im2double(curHeatMap)
            curHeatMap = py_map2jpg(curHeatMap)
            xim = x[ij].reshape(-1, 3)
            xim1 = xim[:, 0].reshape(-1, 299)
            xim2 = xim[:, 1].reshape(-1, 299)
            xim3 = xim[:, 2].reshape(-1, 299)
            image = np.empty([299,299,3])
            image[:, :, 0] = xim1
            image[:, :, 1] = xim2
            image[:, :, 2] = xim3
            a = im2double(image) * 255
            b = im2double(curHeatMap) * 255
            curHeatMap = a * 0.6 + b * 0.4
            ab = np.hstack((a,b))
            full = np.hstack((curHeatMap, ab))
            imname = DIRT + '/' + id + '_' + ddt + '_' + catt + '_ol.png'
            # imname1 = DIRT + '/' + id + '_' + ddt + '_' + catt + '_img.png'
            imname2 = DIRT + '/' + id + '_' + ddt + '_' + catt + '_hm.png'
            # imname3 = DIRT + '/' + id + '_' + ddt + '_' + catt + '_full.png'
            cv2.imwrite(imname, curHeatMap)
            # cv2.imwrite(imname1, a)
            cv2.imwrite(imname2, b)
            # cv2.imwrite(imname3, full)


# CAM for real test; no need to determine correct or wrong
def CAM_R(net, w, pred, x, path, name, bs, rd=0):
    DIRR = "{}/{}_img".format(path, name)
    rd = rd * bs

    try:
        os.mkdir(DIRR)
    except(FileExistsError):
        pass

    pdx = np.asmatrix(pred)

    prl = pdx.argmax(axis=1).astype('uint8')
    camls = []
    for ij in range(len(prl)):
        id = str(ij + rd)
        weights_LR = w
        activation_lastconv = np.array([net[ij]])
        weights_LR = weights_LR.T
        activation_lastconv = activation_lastconv.T

        predNum = 1  # generate heatmap for prediction = which label results
        curCAMmapAll = py_returnCAMmap(activation_lastconv, weights_LR[[predNum], :])
        curCAMmap_crops = curCAMmapAll[:, :, 0]
        curCAMmapLarge_crops = cv2.resize(curCAMmap_crops, (299, 299))
        ### Added Relu ###
        curCAMmapLarge_crops = np.clip(curCAMmapLarge_crops, 0, np.max(curCAMmapLarge_crops))
        ### Added Relu ###
        curHeatMap = cv2.resize(im2double(curCAMmapLarge_crops), (299, 299))  # this line is not doing much
        curHeatMap = im2double(curHeatMap)
        curHeatMap = py_map2jpg(curHeatMap)
        xim = x[ij].reshape(-1, 3)
        xim1 = xim[:, 0].reshape(-1, 299)
        xim2 = xim[:, 1].reshape(-1, 299)
        xim3 = xim[:, 2].reshape(-1, 299)
        image = np.empty([299,299,3])
        image[:, :, 0] = xim1
        image[:, :, 1] = xim2
        image[:, :, 2] = xim3
        a = im2double(image) * 255
        b = im2double(curHeatMap) * 255
        curHeatMap = a * 0.6 + b * 0.4
        ab = np.hstack((a,b))
        full = np.hstack((curHeatMap, ab))
        imname = DIRR + '/' + id + '_ol.png'
        # imname1 = DIRR + '/' + id + '_img.png'
        imname2 = DIRR + '/' + id +'_hm.png'
        # imname3 = DIRR + '/' + id + '_full.png'
        cv2.imwrite(imname, curHeatMap)
        # cv2.imwrite(imname1, a)
        cv2.imwrite(imname2, b)
        # cv2.imwrite(imname3, full)
        camls.append([imname, imname2])

    return np.asarray(camls)


# Output activation for tSNE
def tSNE_prep(flatnet, ori_test, y, pred, path, pmd):
    # format clean up
    tl = np.asmatrix(y)
    tl = tl.argmax(axis=1).astype('uint8')
    pdxt = np.asmatrix(pred)
    prl = pdxt.argmax(axis=1).astype('uint8')
    prl = pd.DataFrame(prl, columns=['Prediction'])
    print(np.shape(flatnet))
    act = pd.DataFrame(np.asmatrix(flatnet))
    if pmd == 'stage':
        outt = pd.DataFrame(pdxt[:, 0:5],
                            columns=['stage0_score', 'stage1_score', 'stage2_score', 'stage3_score', 'stage4_score'])
    elif pmd == "grade":
        outt = pd.DataFrame(pdxt[:, 0:5],
                           columns=['grade0_score', 'grade1_score', 'grade2_score', 'grade3_score', 'grade4_score'])
    elif pmd == "cellularity":
        outt = pd.DataFrame(pdxt[:, 0:3],
                           columns=['0_79_score', '80_89_score', '90_100_score'])
    elif pmd == "nuclei":
        outt = pd.DataFrame(pdxt[:, 0:3],
                           columns=['0_49_score', '50_79_score', '80_100_score'])
    elif pmd == "necrosis":
        outt = pd.DataFrame(pdxt[:, 0:3],
                           columns=['0_score', '1_9_score', '10_100_score'])
    elif pmd == 'origin':
        outt = pd.DataFrame(pdxt[:, 0:10],
                           columns=['HNSCC_score', 'CCRCC_score', 'CO_score', 'BRCA_score', 'LUAD_score', 'LSCC_score',
                                    'PDA_score', 'UCEC_score', 'GBM_score', 'OV_score'])
    else:
        outt = pd.DataFrame(pdxt[:, 0:2], columns=['NEG_score', 'POS_score'])
    outtlt = pd.DataFrame(tl, columns=['True_label'])
    outt.reset_index(drop=True, inplace=True)
    prl.reset_index(drop=True, inplace=True)
    outtlt.reset_index(drop=True, inplace=True)
    out = pd.concat([outt, prl, outtlt], axis=1)
    ori_test.reset_index(drop=True, inplace=True)
    out.reset_index(drop=True, inplace=True)
    act.reset_index(drop=True, inplace=True)
    out = pd.concat([ori_test, out, act], axis=1)
    # if out.shape[0] > 30000:
    #     out = out.sample(30000, replace=False)
    out.to_csv("../Results/{}/out/For_tSNE.csv".format(path), index=False)


