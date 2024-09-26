# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class AgencyItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    name = scrapy.Field()
    description = scrapy.Field()
    link = scrapy.Field()
    projects_starting_at = scrapy.Field()
    rates_starting_at = scrapy.Field()
    tier_level = scrapy.Field()
    years_active = scrapy.Field()
    country = scrapy.Field()
    banner_image_link = scrapy.Field()
    featured_works = scrapy.Field()
    quick_stats_team_members = scrapy.Field()
    quick_stats_certified_developers = scrapy.Field()
    quick_stats_apps_built = scrapy.Field()
    quick_stats_templates = scrapy.Field()
    quick_stats_plugins = scrapy.Field()
    working_with_section_text = scrapy.Field()
    working_with_section_image = scrapy.Field()
    working_with_section_video = scrapy.Field()
    primary_services = scrapy.Field()
    external_profiles = scrapy.Field()
