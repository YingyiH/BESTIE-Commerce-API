from load_config import load_log_conf

LOGGER, _ = load_log_conf()

def product_processing(data, old_data):
    print('DATATATATT', data, old_data)
    if len(data) == 0:
        return 
    new_num_products = old_data['num_products'] + len(data)
    new_max_price = old_data['max_price']
    new_num_onsale_products = old_data['num_onsale_products']

    for product in data:
        LOGGER.info(f"Processing product event: {product['trace_id']}")

        if product['price'] > new_max_price:
            new_max_price = product['price']

        if product['onsale'] == True:
           new_num_onsale_products += 1 

    old_data['num_products'] = new_num_products
    old_data['max_price'] = new_max_price
    old_data['num_onsale_products'] = new_num_onsale_products

def review_processing(data, old_data):
    
    if len(data) == 0:
        return 
    
    new_num_reviews = old_data['num_reviews'] + len(data)

    for review in data:
        LOGGER.debug(f"Processing review event: {review['trace_id']}")


    old_data['num_reviews'] = new_num_reviews
