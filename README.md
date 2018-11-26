[![PyPI version](https://img.shields.io/pypi/v/olx-utils.svg)](https://pypi.python.org/pypi/olx-utils)
[![Build Status](https://travis-ci.org/hastexo/olx-utils.svg?branch=master)](https://travis-ci.org/hastexo/olx-utils)
[![codecov](https://codecov.io/gh/hastexo/olx-utils/branch/master/graph/badge.svg)](https://codecov.io/gh/hastexo/olx-utils)

# OLX Utilities

A set of tools to facilitate courseware development using the
[Open Learning XML](http://edx.readthedocs.io/projects/edx-open-learning-xml/en/latest/)
(OLX) format.

OLX is sometimes tediously repetitive, and this package enables
courseware authors to apply the
[DRY](https://en.wikipedia.org/wiki/Don%27t_repeat_yourself) principle
when writing OLX content. It allows you to define the entire course structure
using a single [YAML](http://yaml.org/) template, and to define and use OLX
templates with [Jinja](http://jinja.pocoo.org/).

`olx-utils` comes with two built-in sequential types:

- `markdown_content`: write courseware content exclusively in
  [Markdown](https://en.wikipedia.org/wiki/Markdown),
- `hastexo_lab`: tailored for use with the
  [hastexo XBlock](https://github.com/hastexo/hastexo-xblock))

## Sample `course.yaml`

What follows is a sample YAML template for a course:

```
parameters:
  name:
    type: string
    default: Course name
  invitation_only:
    type: bool
    default: true
  catalog_visibility:
    type: string
    default: both
  run:
    type: string
  start:
    type: string
  end:
    type: string
  seats:
    type: number

course:
  display_name: { get_param: name }
  url_name: { get_param: run }
  course: ex101
  org: example
  policies:
    policy:
      language: en
      start: { get_param: start }
      advertised_start: { get_param: start }
      end: { get_param: end }
      invitation_only: { get_param: invitation_only }
      catalog_visibility: { get_param: catalog_visibility }
      max_student_enrollments_allowed: { get_param: seats }
      course_image: images_course_image.jpg
      advanced_modules:
        - hastexo
    grading_policy:
      grader:
        - type: Lab
          min_count: 2
          drop_count: 1
          weight: 1.0
      grade_cutoffs:
        pass: 1.0
    assets:
      locked: true
      unlocked:
      - images_course_image.jpg
      - images_course_author.jpg
  global_vars:
    hastexo:
      stack_template_path: hot_lab.yaml
      stack_user_name: training
      stack_protocol: rdp
      providers:
        - name: region1
          capacity: 10
          environment: hot_region1.yaml
        - name: region2
          capacity: -1
          environment: hot_region2.yaml
  chapters:
    - display_name: Chapter 1 Name
      url_name: chapter1
      sequentials:
        - display_name: Section 1
          url_name: section1
          type: markdown_content
          units: 3
        - display_name: Section 1 Lab
          url_name: section1_lab
          type: hastexo_lab
          tests: 2
        - display_name: Section 2
          url_name: section2
          type: markdown_content
          units: 1
        - display_name: Section 2 Lab
          url_name: section2_lab
          type: hastexo_lab
          conditional: chapter1_section1_lab
```

## Install

Install the `olx-utils` package from PyPI:

```bash
pip install olx-utils
```

## Apply templates to a course

In order to create a new course run with 30 seats named `newrun`, starting on
December 1, 2018 and ending on December 31, 2018, simply change into your
courseware checkout, create a new environment file as follows:

```yaml
parameters:
  name: Cool course name (December 2018)
  run: newrun
  start: 2018-12-01
  end: 2018-12-31
  seats: 30
```

Then invoke `olx-new-run`, pointing it to the file you created above:

```bash
olx-new-run --create-branch --environment new_run.yaml
```

The `--create-branch` option causes your rendered OLX to be added to a new Git
branch named `run/newrun`, which you can then import into your Open edX content
store.

## License

This package is licensed under the Affero GPL; see [`LICENSE`](LICENSE) for
details.
