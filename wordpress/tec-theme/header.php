<!DOCTYPE html>
<html <?php language_attributes(); ?>>
<head>
    <meta charset="<?php bloginfo('charset'); ?>">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="profile" href="https://gmpg.org/xfn/11">
    <?php wp_head(); ?>
</head>

<body <?php body_class(); ?>>
<?php wp_body_open(); ?>

<div id="page" class="site">
    <a class="skip-link screen-reader-text" href="#primary"><?php esc_html_e('Skip to content', 'tec-theme'); ?></a>

    <header id="masthead" class="site-header">
        <div class="header-container container">
            <div class="site-branding">
                <?php
                if (has_custom_logo()) :
                    the_custom_logo();
                else :
                ?>
                    <h1 class="site-title"><a href="<?php echo esc_url(home_url('/')); ?>" rel="home"><?php bloginfo('name'); ?></a></h1>
                    <?php
                    $tec_theme_description = get_bloginfo('description', 'display');
                    if ($tec_theme_description || is_customize_preview()) :
                    ?>
                        <p class="site-description"><?php echo $tec_theme_description; ?></p>
                    <?php endif; ?>
                <?php endif; ?>
            </div><!-- .site-branding -->

            <nav id="site-navigation" class="main-navigation">
                <button class="menu-toggle" aria-controls="primary-menu" aria-expanded="false">
                    <span class="menu-toggle-bars">
                        <span class="menu-toggle-bar"></span>
                        <span class="menu-toggle-bar"></span>
                        <span class="menu-toggle-bar"></span>
                    </span>
                    <span class="screen-reader-text"><?php esc_html_e('Menu', 'tec-theme'); ?></span>
                </button>
                <?php
                wp_nav_menu(
                    array(
                        'theme_location' => 'primary',
                        'menu_id'        => 'primary-menu',
                        'container_class' => 'primary-menu-container',
                        'fallback_cb'    => false,
                    )
                );
                ?>
            </nav><!-- #site-navigation -->

            <div class="header-factions">
                <button class="factions-toggle" aria-controls="factions-menu" aria-expanded="false">
                    <span class="faction-icon"></span>
                    <span><?php esc_html_e('Factions', 'tec-theme'); ?></span>
                </button>
                <div class="factions-dropdown">
                    <nav id="factions-navigation" class="factions-navigation">
                        <?php
                        wp_nav_menu(
                            array(
                                'theme_location' => 'factions',
                                'menu_id'        => 'factions-menu',
                                'container_class' => 'factions-menu-container',
                                'fallback_cb'    => 'tec_theme_factions_fallback',
                            )
                        );
                        ?>
                    </nav>
                </div>
            </div>

            <div class="header-crypto-tracker">
                <div class="crypto-tracker-toggle">
                    <span class="crypto-icon"></span>
                    <span class="crypto-price">TEC: $<span class="tec-price">---.--</span></span>
                </div>
                <div class="crypto-tracker-dropdown">
                    <div class="crypto-token-list">
                        <div class="crypto-token" data-token="TEC">
                            <span class="token-name">TEC</span>
                            <span class="token-price">$---.--</span>
                            <span class="token-change">--.--%</span>
                        </div>
                        <div class="crypto-token" data-token="TECRP">
                            <span class="token-name">TECRP</span>
                            <span class="token-price">$---.--</span>
                            <span class="token-change">--.--%</span>
                        </div>
                    </div>
                </div>
            </div>
        </div><!-- .header-container -->
    </header><!-- #masthead -->