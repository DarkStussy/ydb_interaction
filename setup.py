import setuptools

setuptools.setup(
    name='ydb_interaction',
    version='0.0.1',
    author='darkstussy',
    author_email='chornij.stas@gmail.com',
    description='High-level client for YDB interaction',
    url='https://github.com/Darkstussy/ydb_interaction',
    project_urls={
        "Bug Tracker": "https://github.com/Darkstussy/ydb_interaction/issues"
    },
    license='MIT',
    packages=['ydb_interaction'],
    install_requires=['"ydb[yc]"==3.3.4'],
)