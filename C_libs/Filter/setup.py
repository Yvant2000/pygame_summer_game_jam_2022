from setuptools import setup, Extension
# import numpy


def main():
    setup(name="nostalgiaefilters",
          version="1.0.0",
          description="Python interface for the image filter",
          author="Yvant2000",
          author_email="yvant2000@gmail.com",
          ext_modules=[
              Extension(
                  "nostalgiaefilters",
                  ["filter.cpp"],
                  # include_dirs=[numpy.get_include()],
                  extra_compile_args=["/O2", "/GS-", "/fp:fast"]
              )
          ]
          )


if __name__ == "__main__":
    main()
