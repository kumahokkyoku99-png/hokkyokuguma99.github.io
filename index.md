---
layout: home
title: Home
---

<link rel="stylesheet" href="{{ '/assets/css/hero.css' | relative_url }}">

<section class="home-hero" style="--hero-image: url('{{ '/assets/images/hero.jpg' | relative_url }}');">
  <div class="home-hero__content">
    <h1>Polar Bear's Blog</h1>
    <p>Travel · History · Games · Technology</p>
  </div>
</section>

<section class="home-intro">
  <h2>Welcome to my blog!</h2>
  <p>This is my little corner of the internet.</p>
  <p>I write about travel, history, games, drawings, and whatever else happens to interest me.</p>
  <p><a href="{{ '/blog/' | relative_url }}">Browse all posts →</a></p>
</section>

<section class="explore">
  <h2>Explore</h2>
  <p class="explore-intro">Browse topics and discover what interests you.</p>

  <div class="explore-grid">

  <div class="explore-card explore-travel">
      <span class="explore-number">01</span>
      <h3>Travel</h3>
      <p>Places, journeys, landscapes and experiences from around the world.</p>
  </div>

  <div class="explore-card explore-history">
      <span class="explore-number">02</span>
      <h3>History</h3>
      <p>Historical events, cultures, societies and reflections on the past.</p>
    </div>

  <div class="explore-card explore-novel">
      <span class="explore-number">03</span>
      <h3>Novel</h3>
      <p>Fiction, characters, world-building and stories in progress.</p>
    </div>

  <div class="explore-card explore-technology">
      <span class="explore-number">04</span>
      <h3>Technology & Games</h3>
      <p>Programming, technology, games and things I enjoy exploring.</p>
    </div>

  </div>
</section>
{% include latest_posts.html %}