from setuptools import setup

with open('requirements.txt', 'r') as file:
    requirements = file.readlines()

setup(name="save_skype",
      version="0.1.4",
      description="Extract and save Skype chats.",
      url="https://github.com/thismachinechills/save_skype",
      author="thismachinechills (Alex)",
      license="AGPL 3.0",
      packages=['save_skype'],
      zip_safe=True,
      install_requires=requirements,
      keywords="skype main.db extract chats".split(' '),
      entry_points={"console_scripts":
                        ["save_skype = save_skype.extract:chats_to_files"]})
