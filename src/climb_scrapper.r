library(cyclingdata)
data <- cyclingdata

gt_data <- subset(data, race %in% c("Tour de France","Giro d'Italia",'La Vuelta ciclista a España'))

write.csv(gt_data, "grand_tours_all_years.csv", row.names = FALSE)