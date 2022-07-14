from setuptools import setup, Extension


def main():
    setup(name="nostalgiaeraycasting",
          version="1.0.0",
          description="Python raycasting engine for pygame",
          author="Yvant2000",
          author_email="yvant2000@gmail.com",
          ext_modules=[
              Extension(
                  "nostalgiaeraycasting",
                  ["casting.cpp"],
                  extra_compile_args=["/O2", "/GS-", "/fp:fast", "/std:c++latest", "/Zc:strictStrings-"]
              )
          ]
          )


if __name__ == "__main__":
    main()
