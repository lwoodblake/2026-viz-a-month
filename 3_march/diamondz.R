library(tidyverse)
library(ggplot2)
library(patchwork)

#load diamonds dataset and add columns for
#price per carat
#is_perfect for diamonds without flaws
diamondz <- diamonds %>%
  mutate(price_per_carat = (price / carat)) %>%
  mutate(is_perfect = (cut == "Ideal" &
                         clarity == "IF" &
                         color == "D"))

#summarise data
diamondz_summary <- diamondz %>% 
  summarize(total = n(),
            avg_price = mean(price),
            avg_carat = mean(carat),
            avg_price_per_carat = mean(price_per_carat),
            .by = c(cut, color, clarity)) %>%
  arrange(desc(avg_price_per_carat))

#set custom colours for each clarity
clarity_colours = c('IF' = '#2cd8ff',
                    'VVS1' = '#2EC2E5',
                    'VVS2' = '#2EADCB',
                    'VS1' = '#2D98B2',
                    'VS2' = '#2B849A',
                    'SI1' = '#287082',
                    'SI2' = '#255D6C',
                    'I1' = '#214A56')

#scatter plot
scatter <- ggplot(diamondz, aes(x = carat, y = price_per_carat, colour = clarity)) +
  geom_point(shape = 19) +
  scale_color_manual(values = clarity_colours, guide="none") +
  labs(title = "Price x Carat",
       x = 'Carat',
       y = 'Price per Carat') +
  theme(
    panel.background = element_rect(fill = "#FFF5EE"),
    plot.background = element_rect(fill = "#FFF5EE", color="#FFF5EE"),
    panel.border = element_blank(),
    panel.grid = element_blank(),
    axis.line.x = element_line(color="black", size = 0.5),
    axis.line.y = element_line(color="black", size = 0.5),
    plot.title = element_text(size = 18,
                              face = "bold",
                              family = "Palatino"),
    axis.text = element_text(color = "black",
                             size = 12,
                             face = 3,
                             family = "Monaco"),
    text = element_text(family = "Monaco")
  )

#stacked bar
bar <- ggplot(diamondz, aes(y=cut,
                     fill = forcats::fct_rev(clarity))) +
  geom_bar(position = "fill") +
  scale_fill_manual(values = clarity_colours, name = "Clarity") +
  labs(title = "Clarity by Cut") +
  theme(
    panel.background = element_rect(fill = "#FFF5EE"),
    plot.background = element_rect(fill = "#FFF5EE", color="#FFF5EE"),
    panel.border = element_blank(),
    legend.key = element_rect(fill = "#FFF5EE"),
    legend.background = element_rect(color = NA, fill = NA),
    panel.grid = element_blank(),
    axis.title.x=element_blank(),
    axis.title.y=element_blank(),
    axis.text.x=element_blank(),
    axis.ticks.x=element_blank(),
    axis.ticks.y=element_blank(),
    plot.title = element_text(size = 18,
                              face = "bold",
                              family = "Palatino"),
    axis.text = element_text(color = "black",
                             size = 12,
                             face = 3,
                             family = "Monaco"),
    text = element_text(family = "Monaco")
  )

#combine charts into one viz
final_viz <- wrap_plots(scatter | bar) + 
  plot_annotation(title = 'The Diamond Dataset',
                  theme = theme(plot.title = element_text('Imperial Script', size=36)))&
  plot_annotation(theme = theme(plot.background = element_rect(fill ="#FFF5EE", color = "#FFF5EE", linewidth = 1)))

#save viz
ggsave("diamondz.png",
       plot = final_viz,
       width = 10,
       height = 5,
       units = "in",
       dpi=300)
