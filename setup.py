from setuptools import find_packages, setup

setup(
    name='utils',
    packages=find_packages(),

    include_package_data=True,

    package_data={
        "utils": ["dispersion_sims/*.nc"],
    }
)
