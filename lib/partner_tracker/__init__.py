def setup_logging(filename='logging.yml'):
    import yaml
    import logging.config

    try:
        with open(filename, encoding='utf-8') as file:
            logging.config.dictConfig(yaml.load(file.read()))

    except FileNotFoundError:
        print('WARNING: file %s not found, using default logging settings' % filename, file=sys.stderr)
