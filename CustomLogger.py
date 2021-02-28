import logging

def getCustomLogger():
  logger = logging.getLogger("TwitterScrapper")

  c_handler = logging.StreamHandler()
  f_handler = logging.FileHandler("./Logs/TwitterScrapper.log")
  c_handler.setLevel(logging.WARNING)
  f_handler.setLevel(logging.DEBUG)

  c_format = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
  f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
  c_handler.setFormatter(c_format)
  f_handler.setFormatter(f_format)

  logger.addHandler(c_handler)
  logger.addHandler(f_handler)
  return logger