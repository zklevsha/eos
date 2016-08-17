import logging

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# create console handler and set level to info
handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
formatter = logging.Formatter(" %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

handler = logging.FileHandler("log.log")
handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s [%(levelname)s] - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)



logger.info('one')



