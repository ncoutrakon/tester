library(ggplot2); library(reshape2); library(xts); library(scales)
options(stringsAsFactors = F)

# WALLACE
# source("/users/nick/documents/daytrader/funs/fin.R")
# source("/users/nick/documents/daytrader/funs/multiplot.R")
#filename <- "/SierraChart/TradeActivityLogs/SIM_TradesList.txt"

# HUXLEY
#source("/users/ncoutrakon/daytrader/funs/fin.R")
#source("/users/ncoutrakon/daytrader/funs/multiplot.R")
setwd("/users/ncoutrakon/daytrader/reporter")

##################################### MUNGE #############################################
# Reads and formats trades file
filename <- "/users/ncoutrakon/.wine/drive_c/SierraChart/TradeActivityLogs/SIM_TradesList.txt"
trades <- read.table(filename, sep = "\t", header = T)
trades <- trades[, c(1:8)]

# Converts Entry.DateTime and Exit.DateTime to POSIXct
trades[, 3] <- as.POSIXct(trades[, 3])
trades[, 8] <- as.POSIXct(trades[, 8])
trades <- trades[order(trades$Exit.DateTime),]


#tick <- read.table(filename, header = T, sep = ",", colClasses = c("Date", "character", rep("numeric", 8)))
#tick$Time <- as.POSIXct(paste(tick$Date, tick$Time))
filename <- "/users/ncoutrakon/.wine/drive_c/SierraChart/Data/CL_bar.txt"
bar <- read.table(filename, header = T, sep = ",", colClasses = c("Date", "character", rep("numeric", 8)))
bar <- as.xts(bar[, 3:6], order.by = as.POSIXct(paste(bar$Date, bar$Time)))

