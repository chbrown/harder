def ns(*keyparts):
    '''Join the give key parts and namespace them with the global prefix'''
    return ':'.join(['harder'] + list(keyparts))
