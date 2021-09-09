## reduce dimensionality of the acitvation layer of model
## visualize the manifold

# args = commandArgs(trailingOnly=FALSE)
# input_file=args[1]
# output_file=args[2]
# out_fig=args[3]
# start=args[4]
# bins=args[5]
# POS_score=args[6]

### Tile-level tSNE ###
# I START AT 9, X START AT 12; ST start I at 11, X at 14
inlist=c('Results/cellularity_CCA')

for(xx in inlist){
  input_file=paste('~/documents/pancan_imaging/',xx,'/out/For_tSNE.csv',sep='')
  output_file=paste('~/documents/pancan_imaging/',xx,'/out/tSNE_P_N.csv',sep='')
  sampled_file=paste('~/documents/pancan_imaging/',xx,'/out/tSNE_sampled.csv',sep='')
  out_fig=paste('~/documents/pancan_imaging/',xx,'/out/P_N.pdf',sep='')
  start=13
  bins=50
  POS_score=c('0_79_score',	'80_89_score',	'90_100_score')
  TLB = 1 # ST is 2, others 1
  MDP = 0.5 # 0.5 for binary; 1/length(POS_score)
  
  library(Rtsne)
  ori_dat = read.table(file=input_file,header=T,sep=',')
  # P = ori_dat[which(ori_dat$Prediction==1),]
  # N = ori_dat[which(ori_dat$Prediction==0),]
  # N = ori_dat[sample(nrow(N), 20000), ]
  # sp_ori_dat = rbind(P, N)
  # SAMPLE 20000 FOR LEVEL 1 & 2; NO SAMPLE FOR LEVEL 3
  sp_ori_dat=ori_dat[sample(nrow(ori_dat), 20000), ]
  
  write.table(sp_ori_dat, file=sampled_file, row.names = F, sep=',')
  
  X = as.matrix(sp_ori_dat[,start:dim(sp_ori_dat)[2]])
  res = Rtsne(X, initial_dims=100, check_duplicates = FALSE)
  Y=res$Y
  out_dat = cbind(sp_ori_dat[,1:(start-1)],Y)
  
  dat = cbind(out_dat,x_bin=cut(out_dat[,start],bins),
              y_bin=cut(out_dat[,(start+1)],bins))
  
  dat = cbind(dat, x_int = as.numeric(dat$x_bin),
              y_int = as.numeric(dat$y_bin))
  
  colnames(dat)[start:(start+1)]=c('tsne1','tsne2')
  
  dat$True_label=as.factor(dat$True_label)
  dat$Slide_ID=as.factor(dat$Slide_ID)
  
  write.table(dat, file=output_file, row.names = F, sep=',')
  
  
  ## plot the manifold with probability
  library(ggplot2)
  library(gridExtra)
  palist <- list()
  pblist <- list()
  for(i in 1:length(POS_score)){
    palist[[i]]=ggplot(data=dat,aes_string(x='tsne1',y='tsne2',col=paste("X", POS_score[i], sep="")))+
      scale_color_gradient2(high='red',mid='gray',low='steelblue',midpoint=MDP)+
      geom_point(alpha=1, size=1)+ scale_shape(solid = TRUE)+
      xlim(-max(abs(dat$tsne1))*1.1,max(abs(dat$tsne1))*1.1)+
      ylim(-max(abs(dat$tsne2))*1.1,max(abs(dat$tsne2))*1.1)+
      theme_bw() + theme(panel.border = element_blank(), panel.grid.major = element_blank(),
                         panel.grid.minor = element_blank(),
                         axis.line = element_line(colour = "black"), legend.position='bottom')
    
    pblist[[i]]=ggplot(data=dat,aes_string(x='tsne1',y='tsne2'))+
      geom_point(aes(col=Tumor),alpha=0.5)+
      xlim(-max(abs(dat$tsne1))*1.1,max(abs(dat$tsne1))*1.1)+
      ylim(-max(abs(dat$tsne2))*1.1,max(abs(dat$tsne2))*1.1)+
      theme_bw() + theme(panel.border = element_blank(), panel.grid.major = element_blank(),
                         panel.grid.minor = element_blank(),
                         axis.line = element_line(colour = "black"), legend.position='bottom')
  }
  
  pdf(file=out_fig,
      width=14,height=7)
  
  for(i in 1:length(palist)){
    grid.arrange(palist[[i]],pblist[[i]],nrow=1)
  }
  
  dev.off()
  
}


### Slide-level tSNE ###
inlist=c('Results/cellularity_CCA')

for(xx in inlist){
  input_file=paste('~/documents/pancan_imaging/',xx,'/out/For_tSNE.csv',sep='')
  output_file=paste('~/documents/pancan_imaging/',xx,'/out/slide_tSNE_P_N.csv',sep='')
  out_fig=paste('~/documents/pancan_imaging/',xx,'/out/slide_P_N.pdf',sep='')
  out_fig2=paste('~/documents/pancan_imaging/',xx,'/out/slide_circle_P_N.pdf',sep='')
  out_fig3=paste('~/documents/pancan_imaging/',xx,'/out/pred_slide_P_N.pdf',sep='')
  out_fig4=paste('~/documents/pancan_imaging/',xx,'/out/pred_slide_circle_P_N.pdf',sep='')
  start=13
  bins=50
  POS_score=c('0_79_score',	'80_89_score',	'90_100_score')
  tumor_dict = c('0_79_score',	'80_89_score',	'90_100_score')
  TLB = 1 # ST is 2, others 1
  MDP = 0.5 # 0.5 for binary; 1/length(POS_score)
  
  library(dplyr)
  library(Rtsne)
  ori_dat = read.table(file=input_file,header=T,sep=',')
  ori_dat = ori_dat[, c(2,3,8:ncol(ori_dat))]
  sp_ori_dat = ori_dat %>%
    group_by(Slide_ID, Tumor) %>%
    summarise_all(mean) %>%
    mutate(Prediction=round(Prediction))
  sp_ori_dat['Prediction'] = tumor_dict[sp_ori_dat$Prediction+1]
  sp_ori_dat['True_label'] = tumor_dict[sp_ori_dat$True_label+1]
  X = as.matrix(sp_ori_dat[,start:ncol(sp_ori_dat)])
  res = Rtsne(X, initial_dims=100, check_duplicates = FALSE)
  Y=res$Y
  out_dat = cbind.data.frame(sp_ori_dat[,1:start-1],Y)
  dat = cbind(out_dat,x_bin=cut(out_dat[,start],bins),
              y_bin=cut(out_dat[,(start+1)],bins))
  
  dat = cbind(dat, x_int = as.numeric(dat$x_bin),
              y_int = as.numeric(dat$y_bin))
  
  colnames(dat)[start:(start+1)]=c('tsne1','tsne2')
  
  dat$True_label=as.factor(dat$True_label)
  dat$Slide_ID=as.factor(dat$Slide_ID)
  
  write.table(dat, file=output_file, row.names = F, sep=',')
  
  
  ## plot the manifold with probability
  library(ggplot2)
  library(gridExtra)
  library(ggalt)
  library(ggforce)
  palist <- list()
  pblist <- list()
  for(i in 1:length(POS_score)){
    palist[[i]]=ggplot(data=dat,aes_string(x='tsne1',y='tsne2',col=paste("X", POS_score[i], sep="")))+
      scale_color_gradient2(high='red',mid='gray',low='steelblue',midpoint=MDP)+
      geom_point(alpha=1, size=2)+ scale_shape(solid = TRUE)+
      xlim(-max(abs(dat$tsne1))*1.1,max(abs(dat$tsne1))*1.1)+
      ylim(-max(abs(dat$tsne2))*1.1,max(abs(dat$tsne2))*1.1)+
      theme_bw() + theme(panel.border = element_blank(), panel.grid.major = element_blank(),
                         panel.grid.minor = element_blank(),
                         axis.line = element_line(colour = "black"), legend.position='bottom')
    
    pblist[[i]]=ggplot(data=dat,aes_string(x='tsne1',y='tsne2'))+
      geom_point(aes(col=Tumor),alpha=0.5, size=2)+
      xlim(-max(abs(dat$tsne1))*1.1,max(abs(dat$tsne1))*1.1)+
      ylim(-max(abs(dat$tsne2))*1.1,max(abs(dat$tsne2))*1.1)+
      theme_bw() + theme(panel.border = element_blank(), panel.grid.major = element_blank(),
                         panel.grid.minor = element_blank(),
                         axis.line = element_line(colour = "black"), legend.position='bottom')
  }
  
  pdf(file=out_fig,
      width=14,height=7)
  
  for(i in 1:length(palist)){
    grid.arrange(palist[[i]],pblist[[i]],nrow=1)
  }
  
  dev.off()
  
  # ggplot(data=dat,aes_string(x='tsne1',y='tsne2'))+
  #   geom_point(aes(col=Tumor),alpha=0.5, size=3)+
  #   geom_mark_hull(expand=0.03, concavity = 0, aes(fill=Tumor, label=Tumor))+
  # xlim(-max(abs(dat$tsne1))*1.1,max(abs(dat$tsne1))*1.1)+
  # ylim(-max(abs(dat$tsne2))*1.1,max(abs(dat$tsne2))*1.1)+
  #   theme_bw() + theme(panel.border = element_blank(), panel.grid.major = element_blank(),
  #                      panel.grid.minor = element_blank(),
  #                      axis.line = element_line(colour = "black"), legend.position='bottom')
  #
  # ggsave(out_fig2, width=7,height=7)
  
  
  ## plot the manifold with probability
  library(ggplot2)
  library(gridExtra)
  library(ggalt)
  library(ggforce)
  palist <- list()
  pblist <- list()
  for(i in 1:length(POS_score)){
    palist[[i]]=ggplot(data=dat,aes_string(x='tsne1',y='tsne2',col=paste("X", POS_score[i], sep="")))+
      scale_color_gradient2(high='red',mid='gray',low='steelblue',midpoint=MDP)+
      geom_point(alpha=1, size=2)+ scale_shape(solid = TRUE)+
      xlim(-max(abs(dat$tsne1))*1.1,max(abs(dat$tsne1))*1.1)+
      ylim(-max(abs(dat$tsne2))*1.1,max(abs(dat$tsne2))*1.1)+
      theme_bw() + theme(panel.border = element_blank(), panel.grid.major = element_blank(),
                         panel.grid.minor = element_blank(),
                         axis.line = element_line(colour = "black"), legend.position='bottom')
    
    pblist[[i]]=ggplot(data=dat,aes_string(x='tsne1',y='tsne2'))+
      geom_point(aes(col=Prediction),alpha=0.5, size=2)+
      xlim(-max(abs(dat$tsne1))*1.1,max(abs(dat$tsne1))*1.1)+
      ylim(-max(abs(dat$tsne2))*1.1,max(abs(dat$tsne2))*1.1)+
      theme_bw() + theme(panel.border = element_blank(), panel.grid.major = element_blank(),
                         panel.grid.minor = element_blank(),
                         axis.line = element_line(colour = "black"), legend.position='bottom')
  }
  
  pdf(file=out_fig3,
      width=14,height=7)
  
  for(i in 1:length(palist)){
    grid.arrange(palist[[i]],pblist[[i]],nrow=1)
  }
  
  dev.off()
  
  # ggplot(data=dat,aes_string(x='tsne1',y='tsne2'))+
  #   geom_point(aes(col=Prediction),alpha=0.5, size=3)+
  #   geom_mark_hull(expand=0.03, concavity = 0, aes(fill=Prediction, label=Prediction))+
  # xlim(-max(abs(dat$tsne1))*1.1,max(abs(dat$tsne1))*1.1)+
  #   ylim(-max(abs(dat$tsne2))*1.1,max(abs(dat$tsne2))*1.1)+
  #   theme_bw() + theme(panel.border = element_blank(), panel.grid.major = element_blank(),
  #                      panel.grid.minor = element_blank(),
  #                      axis.line = element_line(colour = "black"), legend.position='bottom')
  #
  # ggsave(out_fig4, width=7,height=7)
  
}


### patient-level tSNE ###
inlist=c('Results/cellularity_CCA')

for(xx in inlist){
  input_file=paste('~/documents/pancan_imaging/',xx,'/out/For_tSNE.csv',sep='')
  output_file=paste('~/documents/pancan_imaging/',xx,'/out/patient_tSNE_P_N.csv',sep='')
  out_fig=paste('~/documents/pancan_imaging/',xx,'/out/patient_P_N.pdf',sep='')
  out_fig2=paste('~/documents/pancan_imaging/',xx,'/out/patient_circle_P_N.pdf',sep='')
  out_fig3=paste('~/documents/pancan_imaging/',xx,'/out/pred_patient_P_N.pdf',sep='')
  out_fig4=paste('~/documents/pancan_imaging/',xx,'/out/pred_patient_circle_P_N.pdf',sep='')
  start=13
  bins=50
  POS_score=c('0_79_score',	'80_89_score',	'90_100_score')
  tumor_dict = c('0_79_score',	'80_89_score',	'90_100_score')
  TLB = 1 # ST is 2, others 1
  MDP = 0.5 # 0.5 for binary; 1/length(POS_score)
  
  library(Rtsne)
  library(dplyr)
  ori_dat = read.table(file=input_file,header=T,sep=',')
  ori_dat = ori_dat[, c(1,3,8:ncol(ori_dat))]
  sp_ori_dat = ori_dat %>%
    group_by(Patient_ID, Tumor) %>%
    summarise_all(mean) %>%
    mutate(Prediction=round(Prediction))
  sp_ori_dat['Prediction'] = tumor_dict[sp_ori_dat$Prediction+1]
  sp_ori_dat['True_label'] = tumor_dict[sp_ori_dat$True_label+1]
  X = as.matrix(sp_ori_dat[,start:dim(sp_ori_dat)[2]])
  res = Rtsne(X, initial_dims=100, check_duplicates = FALSE)
  Y=res$Y
  out_dat = cbind.data.frame(sp_ori_dat[,1:(start-1)],Y)
  
  dat = cbind(out_dat,x_bin=cut(out_dat[,start],bins),
              y_bin=cut(out_dat[,(start+1)],bins))
  
  dat = cbind(dat, x_int = as.numeric(dat$x_bin),
              y_int = as.numeric(dat$y_bin))
  
  colnames(dat)[start:(start+1)]=c('tsne1','tsne2')
  
  dat$True_label=as.factor(dat$True_label)
  dat$Patient_ID=as.factor(dat$Patient_ID)
  
  write.table(dat, file=output_file, row.names = F, sep=',')
  
  
  ## plot the manifold with probability
  library(ggplot2)
  library(gridExtra)
  library(ggalt)
  library(ggforce)
  palist <- list()
  pblist <- list()
  for(i in 1:length(POS_score)){
    palist[[i]]=ggplot(data=dat,aes_string(x='tsne1',y='tsne2',col=paste("X", POS_score[i], sep="")))+
      scale_color_gradient2(high='red',mid='gray',low='steelblue',midpoint=MDP)+
      geom_point(alpha=1, size=3)+ scale_shape(solid = TRUE)+
      xlim(-max(abs(dat$tsne1))*1.1,max(abs(dat$tsne1))*1.1)+
      ylim(-max(abs(dat$tsne2))*1.1,max(abs(dat$tsne2))*1.1)+
      theme_bw() + theme(panel.border = element_blank(), panel.grid.major = element_blank(),
                         panel.grid.minor = element_blank(),
                         axis.line = element_line(colour = "black"), legend.position='bottom')
    
    pblist[[i]]=ggplot(data=dat,aes_string(x='tsne1',y='tsne2'))+
      geom_point(aes(col=Tumor),alpha=0.5, size=3)+
      xlim(-max(abs(dat$tsne1))*1.1,max(abs(dat$tsne1))*1.1)+
      ylim(-max(abs(dat$tsne2))*1.1,max(abs(dat$tsne2))*1.1)+
      theme_bw() + theme(panel.border = element_blank(), panel.grid.major = element_blank(),
                         panel.grid.minor = element_blank(),
                         axis.line = element_line(colour = "black"), legend.position='bottom')
  }
  
  pdf(file=out_fig,
      width=14,height=7)
  
  for(i in 1:length(palist)){
    grid.arrange(palist[[i]],pblist[[i]],nrow=1)
  }
  
  dev.off()
  
  
  # ggplot(data=dat,aes_string(x='tsne1',y='tsne2'))+
  #   geom_point(aes(col=Tumor),alpha=0.5, size=3)+
  #   geom_mark_hull(expand=0.03, concavity = 0, aes(fill=Tumor, label=Tumor))+
  # xlim(-max(abs(dat$tsne1))*1.1,max(abs(dat$tsne1))*1.1)+
  #   ylim(-max(abs(dat$tsne2))*1.1,max(abs(dat$tsne2))*1.1)+
  #   theme_bw() + theme(panel.border = element_blank(), panel.grid.major = element_blank(),
  #                      panel.grid.minor = element_blank(),
  #                      axis.line = element_line(colour = "black"), legend.position='bottom')
  #
  # ggsave(out_fig2, width=7,height=7)
  
  
  ## plot the manifold with probability
  library(ggplot2)
  library(gridExtra)
  library(ggalt)
  library(ggforce)
  palist <- list()
  pblist <- list()
  for(i in 1:length(POS_score)){
    palist[[i]]=ggplot(data=dat,aes_string(x='tsne1',y='tsne2',col=paste("X", POS_score[i], sep="")))+
      scale_color_gradient2(high='red',mid='gray',low='steelblue',midpoint=MDP)+
      geom_point(alpha=1, size=3)+ scale_shape(solid = TRUE)+
      xlim(-max(abs(dat$tsne1))*1.1,max(abs(dat$tsne1))*1.1)+
      ylim(-max(abs(dat$tsne2))*1.1,max(abs(dat$tsne2))*1.1)+
      theme_bw() + theme(panel.border = element_blank(), panel.grid.major = element_blank(),
                         panel.grid.minor = element_blank(),
                         axis.line = element_line(colour = "black"), legend.position='bottom')
    
    pblist[[i]]=ggplot(data=dat,aes_string(x='tsne1',y='tsne2'))+
      geom_point(aes(col=Prediction),alpha=0.5, size=3)+
      xlim(-max(abs(dat$tsne1))*1.1,max(abs(dat$tsne1))*1.1)+
      ylim(-max(abs(dat$tsne2))*1.1,max(abs(dat$tsne2))*1.1)+
      theme_bw() + theme(panel.border = element_blank(), panel.grid.major = element_blank(),
                         panel.grid.minor = element_blank(),
                         axis.line = element_line(colour = "black"), legend.position='bottom')
  }
  
  pdf(file=out_fig3,
      width=14,height=7)
  
  for(i in 1:length(palist)){
    grid.arrange(palist[[i]],pblist[[i]],nrow=1)
  }
  
  dev.off()
  
  
  # ggplot(data=dat,aes_string(x='tsne1',y='tsne2'))+
  #   geom_point(aes(col=Prediction),alpha=0.5, size=3)+
  #   geom_mark_hull(expand=0.03, concavity = 0, aes(fill=Prediction, label=Prediction))+
  # xlim(-max(abs(dat$tsne1))*1.1,max(abs(dat$tsne1))*1.1)+
  #   ylim(-max(abs(dat$tsne2))*1.1,max(abs(dat$tsne2))*1.1)+
  #   theme_bw() + theme(panel.border = element_blank(), panel.grid.major = element_blank(),
  #                      panel.grid.minor = element_blank(),
  #                      axis.line = element_line(colour = "black"), legend.position='bottom')
  #
  # ggsave(out_fig4, width=7,height=7)
  
}

