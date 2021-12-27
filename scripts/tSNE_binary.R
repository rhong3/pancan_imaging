## reduce dimensionality of the acitvation layer of model
## visualize the manifold

### Tile-level tSNE ###
inlist=c('Results/TP53_5_CCA')

for(xx in inlist){
  input_file=paste('~/documents/pancan_imaging/',xx,'/out/For_tSNE.csv',sep='')
  output_file=paste('~/documents/pancan_imaging/',xx,'/out/tSNE_P_N.csv',sep='')
  sampled_file=paste('~/documents/pancan_imaging/',xx,'/out/tSNE_sampled.csv',sep='')
  out_fig=paste('~/documents/pancan_imaging/',xx,'/out/P_N.pdf',sep='')
  start=12
  bins=50
  POS_score='POS_score'
  TLB = 1 # ST is 2, others 1
  MDP = 0.5 # 0.5 for binary; 1/length(POS_score)
  
  library(dplyr)
  library(Rtsne)
  ori_dat = read.table(file=input_file,header=T,sep=',')
  sp_ori_dat=ori_dat[sample(nrow(ori_dat), 20000), ]
  write.table(sp_ori_dat, file=sampled_file, row.names = F, sep=',')
  
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
  dat$Prediction=as.factor(dat$Prediction)
  dat$Slide_ID=as.factor(dat$Slide_ID)
  
  write.table(dat, file=output_file, row.names = F, sep=',')
  
  
  ## plot the manifold with probability
  library(ggplot2)
  library(gridExtra)
  library(ggalt)
  library(ggforce)
  
  pa=ggplot(data=dat,aes_string(x='tsne1',y='tsne2',col=POS_score))+
    scale_color_gradient2(high='red',mid='gray',low='steelblue',midpoint=MDP)+
    geom_point(alpha=1, size=2)+ scale_shape(solid = TRUE)+
    xlim(-max(abs(dat$tsne1))*1.1,max(abs(dat$tsne1))*1.1)+
    ylim(-max(abs(dat$tsne2))*1.1,max(abs(dat$tsne2))*1.1)+
    theme_bw() + theme(panel.border = element_blank(), panel.grid.major = element_blank(),
                       panel.grid.minor = element_blank(),
                       axis.line = element_line(colour = "black"), legend.position='bottom')
  
  pb=ggplot(data=dat,aes_string(x='tsne1',y='tsne2'))+
    geom_point(aes(col=Tumor),alpha=0.5, size=2)+
    xlim(-max(abs(dat$tsne1))*1.1,max(abs(dat$tsne1))*1.1)+
    ylim(-max(abs(dat$tsne2))*1.1,max(abs(dat$tsne2))*1.1)+
    theme_bw() + theme(panel.border = element_blank(), panel.grid.major = element_blank(),
                       panel.grid.minor = element_blank(), 
                       axis.line = element_line(colour = "black"), legend.position='bottom')
  
  pc=ggplot(data=dat,aes_string(x='tsne1',y='tsne2'))+
    geom_point(aes(col=True_label),alpha=0.5, size=2)+
    scale_color_manual(values=c('steelblue', 'red')) +
    xlim(-max(abs(dat$tsne1))*1.1,max(abs(dat$tsne1))*1.1)+
    ylim(-max(abs(dat$tsne2))*1.1,max(abs(dat$tsne2))*1.1)+
    theme_bw() + theme(panel.border = element_blank(), panel.grid.major = element_blank(),
                       panel.grid.minor = element_blank(), 
                       axis.line = element_line(colour = "black"), legend.position='bottom')
  
  pd=ggplot(data=dat,aes_string(x='tsne1',y='tsne2'))+
    geom_point(aes(col=Prediction),alpha=0.5, size=2)+
    scale_color_manual(values=c('steelblue', 'red')) +
    xlim(-max(abs(dat$tsne1))*1.1,max(abs(dat$tsne1))*1.1)+
    ylim(-max(abs(dat$tsne2))*1.1,max(abs(dat$tsne2))*1.1)+
    theme_bw() + theme(panel.border = element_blank(), panel.grid.major = element_blank(),
                       panel.grid.minor = element_blank(), 
                       axis.line = element_line(colour = "black"), legend.position='bottom')
  
  pdf(file=out_fig,
      width=14,height=7)
  
  grid.arrange(pa, pb,nrow=1)
  grid.arrange(pc, pd,nrow=1)
  
  dev.off()
  
}

### Slide-level tSNE ###

for(xx in inlist){
  input_file=paste('~/documents/pancan_imaging/',xx,'/out/For_tSNE.csv',sep='')
  output_file=paste('~/documents/pancan_imaging/',xx,'/out/slide_tSNE_P_N.csv',sep='')
  out_fig=paste('~/documents/pancan_imaging/',xx,'/out/slide_P_N.pdf',sep='')
  start=7
  bins=50
  POS_score='POS_score'
  TLB = 1 # ST is 2, others 1
  MDP = 0.5 # 0.5 for binary; 1/length(POS_score)
  
  library(dplyr)
  library(Rtsne)
  ori_dat = read.table(file=input_file,header=T,sep=',')
  ori_dat = na.omit(ori_dat)
  ori_dat = ori_dat[, c(2,3,8:ncol(ori_dat))]
  sp_ori_dat = ori_dat %>%
    group_by(Slide_ID, Tumor) %>%
    summarise_all(mean) %>%
    mutate(Prediction=round(Prediction)) %>%
    mutate(True_label=round(True_label))

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
  dat$Prediction=as.factor(dat$Prediction)
  dat$Slide_ID=as.factor(dat$Slide_ID)
  
  write.table(dat, file=output_file, row.names = F, sep=',')
  
  
  ## plot the manifold with probability
  library(ggplot2)
  library(gridExtra)
  library(ggalt)
  library(ggforce)
  
  pa=ggplot(data=dat,aes_string(x='tsne1',y='tsne2',col=POS_score))+
    scale_color_gradient2(high='red',mid='gray',low='steelblue',midpoint=MDP)+
    geom_point(alpha=1, size=2)+ scale_shape(solid = TRUE)+
    xlim(-max(abs(dat$tsne1))*1.1,max(abs(dat$tsne1))*1.1)+
    ylim(-max(abs(dat$tsne2))*1.1,max(abs(dat$tsne2))*1.1)+
    theme_bw() + theme(panel.border = element_blank(), panel.grid.major = element_blank(),
                       panel.grid.minor = element_blank(),
                       axis.line = element_line(colour = "black"), legend.position='bottom')
    
  pb=ggplot(data=dat,aes_string(x='tsne1',y='tsne2'))+
    geom_point(aes(col=Tumor),alpha=0.5, size=2)+
    xlim(-max(abs(dat$tsne1))*1.1,max(abs(dat$tsne1))*1.1)+
    ylim(-max(abs(dat$tsne2))*1.1,max(abs(dat$tsne2))*1.1)+
    theme_bw() + theme(panel.border = element_blank(), panel.grid.major = element_blank(),
                         panel.grid.minor = element_blank(), 
                         axis.line = element_line(colour = "black"), legend.position='bottom')
  
  pc=ggplot(data=dat,aes_string(x='tsne1',y='tsne2'))+
    geom_point(aes(col=True_label),alpha=0.5, size=2)+
    scale_color_manual(values=c('steelblue', 'red')) +
    xlim(-max(abs(dat$tsne1))*1.1,max(abs(dat$tsne1))*1.1)+
    ylim(-max(abs(dat$tsne2))*1.1,max(abs(dat$tsne2))*1.1)+
    theme_bw() + theme(panel.border = element_blank(), panel.grid.major = element_blank(),
                       panel.grid.minor = element_blank(), 
                       axis.line = element_line(colour = "black"), legend.position='bottom')
  
  pd=ggplot(data=dat,aes_string(x='tsne1',y='tsne2'))+
    geom_point(aes(col=Prediction),alpha=0.5, size=2)+
    scale_color_manual(values=c('steelblue', 'red')) +
    xlim(-max(abs(dat$tsne1))*1.1,max(abs(dat$tsne1))*1.1)+
    ylim(-max(abs(dat$tsne2))*1.1,max(abs(dat$tsne2))*1.1)+
    theme_bw() + theme(panel.border = element_blank(), panel.grid.major = element_blank(),
                       panel.grid.minor = element_blank(), 
                       axis.line = element_line(colour = "black"), legend.position='bottom')
  
  pdf(file=out_fig,
      width=14,height=7)
  
  grid.arrange(pa, pb,nrow=1)
  grid.arrange(pc, pd,nrow=1)
  
  dev.off()
  
}


### patient-level tSNE ###
for(xx in inlist){
  input_file=paste('~/documents/pancan_imaging/',xx,'/out/For_tSNE.csv',sep='')
  output_file=paste('~/documents/pancan_imaging/',xx,'/out/patient_tSNE_P_N.csv',sep='')
  out_fig=paste('~/documents/pancan_imaging/',xx,'/out/patient_P_N.pdf',sep='')
  start=7
  bins=50
  POS_score='POS_score'
  TLB = 1 # ST is 2, others 1
  MDP = 0.5 # 0.5 for binary; 1/length(POS_score)
  
  library(dplyr)
  library(Rtsne)
  ori_dat = read.table(file=input_file,header=T,sep=',')
  ori_dat = na.omit(ori_dat)
  ori_dat = ori_dat[, c(1,3,8:ncol(ori_dat))]
  sp_ori_dat = ori_dat %>%
    group_by(Patient_ID, Tumor) %>%
    summarise_all(mean) %>%
    mutate(Prediction=round(Prediction)) %>%
    mutate(True_label=round(True_label))
  
  X = as.matrix(sp_ori_dat[,start:ncol(sp_ori_dat)])
  res = Rtsne(X, initial_dims=100, check_duplicates = FALSE, perplexity=20)
  Y=res$Y
  out_dat = cbind.data.frame(sp_ori_dat[,1:start-1],Y)
  dat = cbind(out_dat,x_bin=cut(out_dat[,start],bins),
              y_bin=cut(out_dat[,(start+1)],bins))
  
  dat = cbind(dat, x_int = as.numeric(dat$x_bin),
              y_int = as.numeric(dat$y_bin))
  
  colnames(dat)[start:(start+1)]=c('tsne1','tsne2')
  
  dat$True_label=as.factor(dat$True_label)
  dat$Prediction=as.factor(dat$Prediction)
  dat$Patient_ID=as.factor(dat$Patient_ID)
  
  write.table(dat, file=output_file, row.names = F, sep=',')
  
  
  ## plot the manifold with probability
  library(ggplot2)
  library(gridExtra)
  library(ggalt)
  library(ggforce)
  
  pa=ggplot(data=dat,aes_string(x='tsne1',y='tsne2',col=POS_score))+
    scale_color_gradient2(high='red',mid='gray',low='steelblue',midpoint=MDP)+
    geom_point(alpha=1, size=2)+ scale_shape(solid = TRUE)+
    xlim(-max(abs(dat$tsne1))*1.1,max(abs(dat$tsne1))*1.1)+
    ylim(-max(abs(dat$tsne2))*1.1,max(abs(dat$tsne2))*1.1)+
    theme_bw() + theme(panel.border = element_blank(), panel.grid.major = element_blank(),
                       panel.grid.minor = element_blank(),
                       axis.line = element_line(colour = "black"), legend.position='bottom')
  
  pb=ggplot(data=dat,aes_string(x='tsne1',y='tsne2'))+
    geom_point(aes(col=Tumor),alpha=0.5, size=2)+
    xlim(-max(abs(dat$tsne1))*1.1,max(abs(dat$tsne1))*1.1)+
    ylim(-max(abs(dat$tsne2))*1.1,max(abs(dat$tsne2))*1.1)+
    theme_bw() + theme(panel.border = element_blank(), panel.grid.major = element_blank(),
                       panel.grid.minor = element_blank(), 
                       axis.line = element_line(colour = "black"), legend.position='bottom')
  
  pc=ggplot(data=dat,aes_string(x='tsne1',y='tsne2'))+
    geom_point(aes(col=True_label),alpha=0.5, size=2)+
    scale_color_manual(values=c('steelblue', 'red')) +
    xlim(-max(abs(dat$tsne1))*1.1,max(abs(dat$tsne1))*1.1)+
    ylim(-max(abs(dat$tsne2))*1.1,max(abs(dat$tsne2))*1.1)+
    theme_bw() + theme(panel.border = element_blank(), panel.grid.major = element_blank(),
                       panel.grid.minor = element_blank(), 
                       axis.line = element_line(colour = "black"), legend.position='bottom')
  
  pd=ggplot(data=dat,aes_string(x='tsne1',y='tsne2'))+
    geom_point(aes(col=Prediction),alpha=0.5, size=2)+
    scale_color_manual(values=c('steelblue', 'red')) +
    xlim(-max(abs(dat$tsne1))*1.1,max(abs(dat$tsne1))*1.1)+
    ylim(-max(abs(dat$tsne2))*1.1,max(abs(dat$tsne2))*1.1)+
    theme_bw() + theme(panel.border = element_blank(), panel.grid.major = element_blank(),
                       panel.grid.minor = element_blank(), 
                       axis.line = element_line(colour = "black"), legend.position='bottom')
  
  pdf(file=out_fig,
      width=14,height=7)
  
  grid.arrange(pa, pb,nrow=1)
  grid.arrange(pc, pd,nrow=1)
  
  dev.off()
  
}

