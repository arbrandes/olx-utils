What follows is a proposal to further simplify OLX development with `olx-utils` by leveraging YAML and moving from Mako to Jinja2.

# YAML

Instead of having course authors engage OLX templates directly, a task which can be made even more daunting if they have to learn custom template engine jargon, let them define the full course structure using a single YAML file, such as the following one.

```yaml
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
      default_locked: true
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

## Params and functions

Parameters and built-in functions work as they do in OpenStack Heat templates (from whence inspiration for this came).

## Global vars

It is possible to specify global variables that will be presented as context to any templates.

## Assets

In keeping with the idea of simplication, and taking into account the fact that upon OLX import edX will find assets on its own, the only assets that need be defined are the exceptions to the defined rule.  If they are all locked (`default_locked`: true), one can specify unlocked ones via the `unlocked` item, or `locked` if not.

## Sequential Types

Two sequential types will be implemented:

### `markdown_content`

When set for a sequential along with a corresponding `units` count, the `markdown` top level directory of a course will be scoured for `units` file names that begin with the `url_name` property of the sequential, suffixed with `_unit_{number}.md`.  The following will happen for each file:

1. It will be treated as a Jinja template, and rendered into an equally named file in `static/markdown`.
2. Based on the Jinja-rendered markdown file, the markdown content will be converted into a correspondingly named HTML file, linked appropriately into the rest of the course structure, in the `html` top level directory.
3. Every rendered markdown file will be tracked in a globally available `markdown_content` list, exposed as a context variable to custom templates.  (Useful, for example, in a reveal.js presentation index.)

Markdown files can use the `asset_url()` helper to render image URLs in the way that edX expects them.

### `hastexo_lab`

This will create a section that uses the `hastexo:` YAML global var to render a hastexo XBlock invocation with a set of instructions and progress checks.  Instructions will be rendered much like `markdown_content`, but this section is limited to a single markdown file, named `{url_name}_instructions.md`.  (This file will _not_ be included in the `markdown_content` list.)

This section takes a `tests` count.  If defined, `olx-utils` will walk the `hastexo` directory looking for any files that begin with the sequential's `url_name` and end as `_test_{number}.{sh|py}`.  They will be taken in sequence and included as hastexo XBlock progress checks for this section.

If a `conditional` is defined for the section, it must point to the `url_name` of a previous `hastexo_lab` section.

# Jinja

In the common use case the course author should be exposed to not only as little XML as possible, but as little template syntax as possible.  Jinja is much cleaner than Mako.  For example, with Mako, it was necessary to include unwieldy headers such as `<%namespace file="/olx_partials.xml" import="asset_url"/>\` in all templates, including markdown files.  Jinja will let us do away with that.

Furthermore, Mako syntax is too brittle.  For instance, there's no clean way to tell it that in markdown files, `##` is not a comment and should not be processed.  Jinja makes this configurable, and should thus allow for cleaner markdown.

## Custom templates

The proposed YAML syntax lets a user to define custom templates and global variables.  This allows for the following:

### Custom tabs

By specifying the following YAML, one can substitute the built-in edX forum with Disqus, for example:


```yaml
  policies:
    policy:
      tabs:
        - name: Discussion
          type: static_tab
          url_slug: discussion
  custom_templates:
    - dir: tabs
      ext: html
  global_vars:
    disqus:
      url: { get_param: disqus_url }
      identifier: { get_param: disqus_identifier }
```

Creating a `tabs/discussion.html` with Jinja substitution for url and identifier should work after rendering.

### Reveal.js for courseware presentation

To use reveal.js as a presentation engine for the rendered markdown, one can do the following:

1. Include the desired version of reveal.js and plugins into `static/presentation`.
2. Add the following custom template:

```yaml
  custom_templates:
    - dir: static/presentation
      ext: html
```

3. Use the `markdown_content` built-in Jinja global var in `static/presentation/index.html` to render all slides:

```html
<div class="slides">
  {% for markdown_file in markdown_content %}
  <section data-markdown="/{{ asset_url(markdown_file) }}"
           data-separator="^\n\n\n"
           data-separator-vertical="^\n\n"
           data-separator-notes="^<!-- Note -->">
  </section>
  {% endfor %}
</div>
```

# Directory structure

The source directory structure of the simplest use case should be no more complicated than:

```bash
course/
  hastexo/
    section1_lab_test_01.sh
    section1_lab_test_02.sh
    ...
  markdown/
    section1_lab_instructions.md
    section1_unit_01.md
    section1_unit_02.md
    ...
  static/
    images/
      course_image.jpg
      diagram1.svg
      ...
    hot/
      lab.yaml
      region1.yaml
      ...
  course.yaml

```

Note the absence of any symlinks or other OLX boilerplate.

# Invocation

In order to create a new course run with 30 seats named `newrun`, starting on December 1, 2018 and ending on December 31, 2018, simply change into your courseware checkout, create a new environment file as follows:

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

The `--create-branch` option causes your rendered OLX to be added to a new Git branch named `run/newrun`, which you can then import into your Open edX content store.

# Backward compatibility

No backward compatibility is proposed, here.  Old courseware should just use the `0.0.x` branch of `olx-utils`.
