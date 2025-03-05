---
layout: page
title: Legit Feed
subtitle: The Place to get all your Full Legit Party POVs
---
<!-- Link to another page -->
<p><a href="https://thenose2003.github.io/legitleaderboard/">Full Legit Party Leaderboard</a></p>

{% for post in site.categories.legitPlayer %}
- [{{ post.title }}]({{ post.url }})
{% endfor %}
