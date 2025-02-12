"""
Setup discopy package.
"""

if __name__ == '__main__':  # pragma: no cover
    from re import search, M
    from setuptools import setup, find_packages

    def get_version(filename="discopy/__init__.py",
                    pattern=r"^__version__ = ['\"]([^'\"]*)['\"]"):
        with open(filename, 'r') as file:
            MATCH = search(pattern, file.read(), M)
            if MATCH:
                return MATCH.group(1)
            else:
                raise RuntimeError("Unable to find version string.")

    VERSION = get_version()

    def get_reqs(filename):
        try:
            with open(filename, 'r') as file:
                return [line.strip() for line in file.readlines()]
        except FileNotFoundError:
            from warnings import warn
            warn("{} not found".format(filename))
            return []

    TEST_REQS = get_reqs("test/requirements.txt")
    DOCS_REQS = get_reqs("docs/requirements.txt")

    setup(name='discopy',
          version=VERSION,
          package_dir={'discopy': 'discopy'},
          packages=find_packages(),
          description='Distributional Compositional Python',
          long_description=open("README.md", "r").read(),
          long_description_content_type="text/markdown",
          url='https://github.com/oxford-quantum-group/discopy',
          author='Alexis Toumi',
          author_email='alexis.toumi@cs.ox.ac.uk',
          download_url='https://github.com/'
                       'oxford-quantum-group/discopy/archive/'
                       '{}.tar.gz'.format(VERSION),
          install_requires=[
              l.strip() for l in open('requirements.txt').readlines()],
          tests_require=TEST_REQS,
          extras_require={'test': TEST_REQS, 'docs': DOCS_REQS},
          data_file=[('test', ['test/requirements.txt']),
                     ('docs', ['docs/requirements.txt'])],
          python_requires='>=3',
          )
