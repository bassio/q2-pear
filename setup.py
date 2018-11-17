from setuptools import setup, find_packages


setup(
    name="q2-pear",
    version="0.01",
    packages=find_packages(),
    author="Ahmed Bassiouni",
    author_email="ahmedbassi@gmail.com",
    description="QIIME 2 plugin for joining paired end reads using PEAR (Zhang et al.).",
    license='BSD-3-Clause',
    url="https://github.com/bassio/q2-pear",
    entry_points={
        "qiime2.plugins":
        ["q2-pear=q2_pear.plugin_setup:plugin"]
    },
    package_data={
        'q2_pear': ['citations.bib']
        },
    zip_safe=False,
) 
 
