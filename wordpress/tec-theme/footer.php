    <footer id="colophon" class="site-footer">
        <div class="footer-widgets-area">
            <div class="container">
                <div class="footer-widgets-wrapper">
                    <?php if (is_active_sidebar('footer-widgets')) : ?>
                        <?php dynamic_sidebar('footer-widgets'); ?>
                    <?php endif; ?>
                </div>
            </div>
        </div>
        
        <div class="site-info">
            <div class="container">
                <div class="footer-factions-logo">
                    <div class="factions-grid">
                        <?php
                        $factions_data = tec_get_factions_data();
                        if (!empty($factions_data['factions'])) {
                            foreach (array_slice($factions_data['factions'], 0, 6) as $faction) {
                                $faction_name = esc_html($faction['name']);
                                $faction_slug = sanitize_title($faction_name);
                                $faction_color = isset($faction['colors'][0]) ? esc_attr($faction['colors'][0]) : 'currentColor';
                                
                                echo '<div class="faction-icon-small faction-' . $faction_slug . '" 
                                          title="' . $faction_name . '"
                                          style="--faction-color: ' . $faction_color . ';">
                                      </div>';
                            }
                        }
                        ?>
                    </div>
                </div>
                
                <div class="footer-navigation">
                    <?php
                    wp_nav_menu(
                        array(
                            'theme_location' => 'footer',
                            'menu_id'        => 'footer-menu',
                            'container_class' => 'footer-menu-container',
                            'depth'          => 1,
                            'fallback_cb'    => false,
                        )
                    );
                    ?>
                </div>
                
                <div class="copyright-info">
                    <p>
                        &copy; <?php echo date('Y'); ?> 
                        <a href="<?php echo esc_url(home_url('/')); ?>"><?php bloginfo('name'); ?></a>.
                        <?php esc_html_e('All rights reserved.', 'tec-theme'); ?>
                    </p>
                </div>
                
                <div class="crypto-badges">
                    <span class="crypto-badge eth">ETH</span>
                    <span class="crypto-badge xrp">XRP</span>
                    <span class="crypto-badge ada">ADA</span>
                </div>
            </div>
        </div><!-- .site-info -->
    </footer><!-- #colophon -->
</div><!-- #page -->

<?php wp_footer(); ?>

</body>
</html>