# super correlation between tumor model and mutations. 
library(readr)
tumor = read_csv('Results/tumor/out/For_tsne.csv')
tumor = tumor[tumor$label == 1,]
tumor = tumor[,-c(1,3:11)]

tumor_ag = aggregate(tumor[,2:2689], list(tumor$Slide_ID), mean)
colnames(tumor_ag)[1] = 'Slide_ID'

mutation = read_csv('mutation_label.csv')
mutation = mutation[mutation$Slide_ID %in% tumor_ag$Slide_ID,]
tumor_ag = tumor_ag[tumor_ag$Slide_ID %in% mutation$Slide_ID,]
tumor_ag = tumor_ag[order(tumor_ag$Slide_ID), ]
mutation = mutation[order(mutation$Slide_ID), ]
mutation = mutation[, -c(1, 3)]

mgg = merge(tumor_ag, mutation, by='Slide_ID')
xxx = mgg$Slide_ID
mgg = mgg[,-1]
rownames(mgg)=xxx

res <- cor(mgg)
res = round(res, 2)
res = res[1:2688, 2689:23405]

resdf = abs(res)
resdf[is.na(resdf)] = 0

write.csv(resdf, file = "~/documents/pancan_imaging/Results/tumor/mut_corr.csv", row.names=TRUE)

mmm= colnames(resdf)[unlist(apply(resdf,1,which.max))]

write.csv(data.frame(mmm), file = "~/documents/pancan_imaging/Results/tumor/mut_corr_max.csv")
write.csv(data.frame(unique(mmm)), file = "~/documents/pancan_imaging/Results/tumor/mut_corr_max_uniq.csv", row.names=FALSE)

