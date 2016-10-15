from setuptools import setup


setup(name="save_skype",
      version="0.1",
      description="Extract and save Skype chats.",
      url="https://github.com/thismachinechills/save_skype",
      author="thismachinechills (Alex)",
      license="AGPL 3.0",
      packages=['save_skype'],
      zip_safe=True,
      install_requires=["click", "html_wrapper"],
      keywords="skype main.db extract chats".split(' '),
      entry_points={"console_scripts":
                        ["save_skype = save_skype.extract:cmd"]})
