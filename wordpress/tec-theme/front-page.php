<?php
/**
 * The template for displaying the front page
 *
 * @package TEC_Theme
 */

get_header();
?>

<main id="primary" class="site-main front-page">
    <!-- Hero Section with Dynamic Faction-themed Background -->
    <section class="tec-hero">
        <div class="hero-background">
            <div class="faction-overlay"></div>
        </div>
        <div class="container">
            <div class="hero-content">
                <h1 class="hero-title"><?php echo esc_html(get_bloginfo('name')); ?></h1>
                <p class="hero-tagline"><?php echo esc_html(get_bloginfo('description')); ?></p>
                <div class="hero-cta">
                    <a href="<?php echo esc_url(home_url('/lore')); ?>" class="btn btn-primary">Explore The Lore</a>
                    <a href="<?php echo esc_url(home_url('/factions')); ?>" class="btn btn-secondary">Join A Faction</a>
                </div>
            </div>
        </div>
    </section>

    <!-- Featured Factions Section -->
    <section class="tec-factions">
        <div class="container">
            <h2 class="section-title">Featured Factions</h2>
            <div class="factions-grid">
                <?php
                $factions_data = tec_get_factions_data();
                if (!empty($factions_data['factions'])) {
                    // Display up to 4 featured factions
                    foreach (array_slice($factions_data['factions'], 0, 4) as $faction) {
                        ?>
                        <div class="faction-card">
                            <div class="faction-card-header" style="--faction-primary: <?php echo isset($faction['colors'][0]) ? esc_attr($faction['colors'][0]) : '#000'; ?>; --faction-secondary: <?php echo isset($faction['colors'][1]) ? esc_attr($faction['colors'][1]) : '#fff'; ?>;">
                                <h3 class="faction-name"><?php echo esc_html($faction['name']); ?></h3>
                            </div>
                            <div class="faction-card-content">
                                <p class="faction-description"><?php echo esc_html($faction['description']); ?></p>
                                <div class="faction-ethos">
                                    <blockquote>"<?php echo esc_html($faction['ethos']); ?>"</blockquote>
                                </div>
                            </div>
                            <div class="faction-card-footer">
                                <a href="<?php echo esc_url(home_url('/faction/' . sanitize_title($faction['name']))); ?>" class="faction-link">Learn More</a>
                            </div>
                        </div>
                        <?php
                    }
                } else {
                    echo '<p>No faction data available.</p>';
                }
                ?>
            </div>
            <div class="section-cta">
                <a href="<?php echo esc_url(home_url('/factions')); ?>" class="btn btn-outline">View All Factions</a>
            </div>
        </div>
    </section>

    <!-- Latest Articles Section -->
    <section class="tec-latest-articles">
        <div class="container">
            <h2 class="section-title">Latest from The Codex</h2>
            <div class="articles-grid">
                <?php
                $latest_posts_args = array(
                    'post_type' => 'post',
                    'posts_per_page' => 3,
                    'ignore_sticky_posts' => true,
                );
                
                $latest_posts_query = new WP_Query($latest_posts_args);
                
                if ($latest_posts_query->have_posts()) :
                    while ($latest_posts_query->have_posts()) : $latest_posts_query->the_post();
                        ?>
                        <article class="article-card">
                            <?php if (has_post_thumbnail()) : ?>
                                <div class="article-image">
                                    <a href="<?php the_permalink(); ?>">
                                        <?php the_post_thumbnail('medium'); ?>
                                    </a>
                                </div>
                            <?php endif; ?>
                            <div class="article-content">
                                <h3 class="article-title"><a href="<?php the_permalink(); ?>"><?php the_title(); ?></a></h3>
                                <div class="article-meta">
                                    <?php
                                    // Get faction association if exists
                                    $faction_association = get_post_meta(get_the_ID(), '_tec_faction_association', true);
                                    if (!empty($faction_association)) :
                                        echo '<span class="article-faction">' . esc_html($faction_association) . '</span>';
                                    endif;
                                    ?>
                                    <span class="article-date"><?php echo get_the_date(); ?></span>
                                </div>
                                <div class="article-excerpt">
                                    <?php the_excerpt(); ?>
                                </div>
                                <a href="<?php the_permalink(); ?>" class="read-more">Read More</a>
                            </div>
                        </article>
                        <?php
                    endwhile;
                    wp_reset_postdata();
                else :
                    echo '<p>No posts found</p>';
                endif;
                ?>
            </div>
            <div class="section-cta">
                <a href="<?php echo esc_url(home_url('/blog')); ?>" class="btn btn-outline">View All Articles</a>
            </div>
        </div>
    </section>

    <!-- TEC Crypto Tracker -->
    <section class="tec-crypto-section">
        <div class="container">
            <h2 class="section-title">TEC Crypto Tracker</h2>
            <div class="crypto-dashboard">
                <div class="token-cards">
                    <div class="token-card tec-token">
                        <div class="token-header">
                            <h3 class="token-name">TEC</h3>
                            <span class="token-network">ETH</span>
                        </div>
                        <div class="token-price">
                            <span class="price-value">$---.--</span>
                            <span class="price-change">--.--%</span>
                        </div>
                        <div class="token-chart">
                            <!-- Placeholder for chart -->
                            <div class="chart-placeholder"></div>
                        </div>
                        <div class="token-footer">
                            <a href="<?php echo esc_url(home_url('/crypto/tec')); ?>" class="token-details-link">View Details</a>
                        </div>
                    </div>
                    <div class="token-card tecrp-token">
                        <div class="token-header">
                            <h3 class="token-name">TECRP</h3>
                            <span class="token-network">XRP</span>
                        </div>
                        <div class="token-price">
                            <span class="price-value">$---.--</span>
                            <span class="price-change">--.--%</span>
                        </div>
                        <div class="token-chart">
                            <!-- Placeholder for chart -->
                            <div class="chart-placeholder"></div>
                        </div>
                        <div class="token-footer">
                            <a href="<?php echo esc_url(home_url('/crypto/tecrp')); ?>" class="token-details-link">View Details</a>
                        </div>
                    </div>
                </div>
                <div class="crypto-events">
                    <h3 class="crypto-events-title">Recent Crypto Events</h3>
                    <div class="events-list">
                        <?php
                        $crypto_events_args = array(
                            'post_type' => 'crypto_event',
                            'posts_per_page' => 3,
                        );
                        
                        $crypto_events_query = new WP_Query($crypto_events_args);
                        
                        if ($crypto_events_query->have_posts()) :
                            while ($crypto_events_query->have_posts()) : $crypto_events_query->the_post();
                                ?>
                                <div class="event-item">
                                    <div class="event-date"><?php echo get_the_date('M d'); ?></div>
                                    <div class="event-content">
                                        <h4 class="event-title">
                                            <a href="<?php the_permalink(); ?>"><?php the_title(); ?></a>
                                        </h4>
                                        <div class="event-excerpt"><?php the_excerpt(); ?></div>
                                    </div>
                                </div>
                                <?php
                            endwhile;
                            wp_reset_postdata();
                        else :
                            echo '<p>No crypto events found</p>';
                        endif;
                        ?>
                    </div>
                    <a href="<?php echo esc_url(home_url('/crypto-events')); ?>" class="all-events-link">View All Events</a>
                </div>
            </div>
        </div>
    </section>

    <!-- Call to Join -->
    <section class="tec-call-to-join">
        <div class="container">
            <div class="join-content">
                <h2 class="join-title">Join The Elidoras Codex</h2>
                <p class="join-description">Become part of the narrative. Choose your faction. Shape the lore. Track the tokens. Build the future.</p>
                <div class="join-buttons">
                    <a href="<?php echo esc_url(home_url('/register')); ?>" class="btn btn-primary">Register Now</a>
                    <a href="<?php echo esc_url(home_url('/about')); ?>" class="btn btn-secondary">Learn More</a>
                </div>
            </div>
            <div class="join-decoration">
                <div class="faction-icons">
                    <?php
                    if (!empty($factions_data['factions'])) {
                        foreach (array_slice($factions_data['factions'], 0, 6) as $index => $faction) {
                            $delay = $index * 0.2;
                            $faction_name = esc_html($faction['name']);
                            $faction_slug = sanitize_title($faction_name);
                            echo '<div class="faction-icon faction-' . $faction_slug . '" style="animation-delay: ' . $delay . 's;"></div>';
                        }
                    }
                    ?>
                </div>
            </div>
        </div>
    </section>
</main>

<?php get_footer(); ?>