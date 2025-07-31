def is_relevant_article(region, text):
    text = text.lower()
    region = region.lower()
    
    if region == 'china':
        return 'china' in text or 'chinese' in text
    elif region == 'middle_east':
        middle_east_countries = ['middle east', 'iran', 'iraq', 'jordan', 'kuwait', 'lebanon', 'oman', 'palestine', 'qatar', 
                                 'saudi arabia', 'syria', 'united arab emirates', 'uae', 'yemen', 'türkiye', 'turkey']
        return any(country in text for country in middle_east_countries)
    elif region == 'central_asia':
        central_asia_countries = ['central asia', 'kazakhstan', 'kyrgyzstan', 'tajikistan', 'turkmenistan', 'uzbekistan']
        return any(country in text for country in central_asia_countries)
    elif region == 'latin_america':
        latin_america_countries = ['latin america', 'argentina', 'bolivia', 'brazil', 'chile', 'colombia', 'costa rica', 
                                   'cuba', 'dominican republic', 'ecuador', 'el salvador', 'guatemala', 'honduras', 'mexico', 
                                   'nicaragua', 'panama', 'paraguay', 'peru', 'puerto rico', 'uruguay', 'venezuela']
        return any(country in text for country in latin_america_countries)
    elif region == 'africa':
        african_countries = [
            'africa', 'algeria', 'angola', 'benin', 'botswana', 'burkina faso', 'burundi', 
            'cape verde', 'cameroon', 'central african republic', 'chad', 'comoros', 
            'democratic republic of the congo', 'djibouti', 'egypt', 'equatorial guinea', 
            'eritrea', 'eswatini', 'ethiopia', 'gabon', 'gambia', 'ghana', 'guinea', 
            'guinea-bissau', 'ivory coast', 'kenya', 'lesotho', 'liberia', 'libya', 'madagascar', 
            'malawi', 'mali', 'mauritania', 'mauritius', 'morocco', 'mozambique', 'namibia', 
            'niger', 'nigeria', 'rwanda', 'sao tome and principe', 'senegal', 'seychelles', 
            'sierra leone', 'somalia', 'south africa', 'south sudan', 'sudan', 'tanzania', 
            'togo', 'tunisia', 'uganda', 'zambia', 'zimbabwe'
        ]
        return any(country in text for country in african_countries)
    elif region == 'southeast_asia':
        southeast_asia_countries = [
            'southeast asia', 'brunei', 'cambodia', 'east timor', 'indonesia', 'laos', 
            'malaysia', 'myanmar', 'philippines', 'singapore', 'thailand', 'vietnam'
        ]
        return any(country in text for country in southeast_asia_countries)
    return False

# 定义筛选函数
def filter_news_by_region(news_list, region):
    filtered_list = []
    for news in news_list:
        if is_relevant_article(region.lower(), news['title'].lower()) or is_relevant_article(region.lower(), news['abstract'].lower()):
            filtered_list.append(news)
    return filtered_list
