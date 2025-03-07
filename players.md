---
layout: page
title: "Players"
---
{% for post in site.posts %}
  {% if post.tags contains "books" %}
    ## [{{ post.title }}]({{ post.url }})
    {{ post.excerpt }}
  {% endif %}
{% endfor %}
