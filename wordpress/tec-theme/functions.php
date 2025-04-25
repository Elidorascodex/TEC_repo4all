<?php
/**
 * TEC Theme Functions
 * 
 * @package TEC_Theme
 */

// Exit if accessed directly
if (!defined('ABSPATH')) {
    exit;
}

// Define constants
define('TEC_THEME_VERSION', '1.0.0');
define('TEC_THEME_DIR', get_template_directory());
define('TEC_THEME_URI', get_template_directory_uri());

/**
 * Theme Setup Functions
 */
function tec_theme_setup() {
    // Add theme support
    add_theme_support('title-tag');
    add_theme_support('automatic-feed-links');
    add_theme_support('post-thumbnails');
    add_theme_support('custom-logo', array(
        'height'      => 100,
        'width'       => 300,
        'flex-height' => true,
        'flex-width'  => true,
    ));
    add_theme_support('html5', array(
        'search-form',
        'comment-form',
        'comment-list',
        'gallery',
        'caption',
    ));
    add_theme_support('customize-selective-refresh-widgets');
    add_theme_support('responsive-embeds');
    add_theme_support('custom-header');
    add_theme_support('editor-styles');
    add_theme_support('wp-block-styles');
    add_theme_support('align-wide');

    // Register navigation menus
    register_nav_menus(array(
        'primary' => __('Primary Menu', 'tec-theme'),
        'footer'  => __('Footer Menu', 'tec-theme'),
        'factions' => __('Factions Menu', 'tec-theme'),
    ));
}
add_action('after_setup_theme', 'tec_theme_setup');

/**
 * Register and Enqueue Styles/Scripts
 */
function tec_theme_enqueue_scripts() {
    // Styles
    wp_enqueue_style('google-fonts', 'https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;600;700&family=Poppins:wght@300;400;500;600;700&family=Source+Code+Pro:wght@400;500&display=swap', array(), null);
    wp_enqueue_style('tec-theme-style', get_stylesheet_uri(), array(), TEC_THEME_VERSION);
    
    // Additional CSS files
    wp_enqueue_style('tec-factions-style', TEC_THEME_URI . '/assets/css/factions.css', array(), TEC_THEME_VERSION);
    wp_enqueue_style('tec-crypto-style', TEC_THEME_URI . '/assets/css/crypto-tracker.css', array(), TEC_THEME_VERSION);
    
    // Scripts
    wp_enqueue_script('tec-navigation', TEC_THEME_URI . '/assets/js/navigation.js', array('jquery'), TEC_THEME_VERSION, true);
    wp_enqueue_script('tec-main', TEC_THEME_URI . '/assets/js/main.js', array('jquery'), TEC_THEME_VERSION, true);
    
    // Conditionally load scripts
    if (is_front_page()) {
        wp_enqueue_script('tec-home', TEC_THEME_URI . '/assets/js/home.js', array('jquery'), TEC_THEME_VERSION, true);
    }
    
    // Add crypto tracking scripts if needed
    if (is_page_template('templates/crypto-dashboard.php') || is_front_page()) {
        wp_enqueue_script('chart-js', 'https://cdn.jsdelivr.net/npm/chart.js@3.7.0/dist/chart.min.js', array(), '3.7.0', true);
        wp_enqueue_script('tec-crypto-tracker', TEC_THEME_URI . '/assets/js/crypto-tracker.js', array('jquery', 'chart-js'), TEC_THEME_VERSION, true);
        
        // Localize script for API endpoints
        wp_localize_script('tec-crypto-tracker', 'tecCryptoData', array(
            'apiUrl' => rest_url('tec/v1/crypto'),
            'nonce' => wp_create_nonce('wp_rest'),
        ));
    }
}
add_action('wp_enqueue_scripts', 'tec_theme_enqueue_scripts');

/**
 * Register widget areas
 */
function tec_theme_widgets_init() {
    // Main Sidebar
    register_sidebar(array(
        'name'          => __('Main Sidebar', 'tec-theme'),
        'id'            => 'sidebar-1',
        'description'   => __('Add widgets here to appear in your sidebar.', 'tec-theme'),
        'before_widget' => '<div id="%1$s" class="widget %2$s">',
        'after_widget'  => '</div>',
        'before_title'  => '<h3 class="widget-title">',
        'after_title'   => '</h3>',
    ));
    
    // Footer Widgets
    for ($i = 1; $i <= 4; $i++) {
        register_sidebar(array(
            'name'          => __('Footer Widget ' . $i, 'tec-theme'),
            'id'            => 'footer-' . $i,
            'description'   => __('Add widgets here to appear in footer column ' . $i, 'tec-theme'),
            'before_widget' => '<div id="%1$s" class="widget %2$s">',
            'after_widget'  => '</div>',
            'before_title'  => '<h3 class="widget-title">',
            'after_title'   => '</h3>',
        ));
    }
}
add_action('widgets_init', 'tec_theme_widgets_init');

/**
 * Faction Post Type and Taxonomy Setup
 */
function tec_theme_register_post_types() {
    // Register Faction Post Type
    register_post_type('tec_faction', array(
        'labels' => array(
            'name'                  => __('Factions', 'tec-theme'),
            'singular_name'         => __('Faction', 'tec-theme'),
            'add_new'               => __('Add New', 'tec-theme'),
            'add_new_item'          => __('Add New Faction', 'tec-theme'),
            'edit_item'             => __('Edit Faction', 'tec-theme'),
            'new_item'              => __('New Faction', 'tec-theme'),
            'view_item'             => __('View Faction', 'tec-theme'),
            'search_items'          => __('Search Factions', 'tec-theme'),
            'not_found'             => __('No factions found', 'tec-theme'),
            'not_found_in_trash'    => __('No factions found in Trash', 'tec-theme'),
        ),
        'public'              => true,
        'has_archive'         => true,
        'menu_icon'           => 'dashicons-groups',
        'supports'            => array('title', 'editor', 'thumbnail', 'excerpt', 'custom-fields'),
        'rewrite'             => array('slug' => 'factions'),
        'show_in_rest'        => true,
        'menu_position'       => 5,
    ));
    
    // Register Cryptocurrency Post Type
    register_post_type('tec_token', array(
        'labels' => array(
            'name'                  => __('Tokens', 'tec-theme'),
            'singular_name'         => __('Token', 'tec-theme'),
            'add_new'               => __('Add New', 'tec-theme'),
            'add_new_item'          => __('Add New Token', 'tec-theme'),
            'edit_item'             => __('Edit Token', 'tec-theme'),
            'new_item'              => __('New Token', 'tec-theme'),
            'view_item'             => __('View Token', 'tec-theme'),
            'search_items'          => __('Search Tokens', 'tec-theme'),
            'not_found'             => __('No tokens found', 'tec-theme'),
            'not_found_in_trash'    => __('No tokens found in Trash', 'tec-theme'),
        ),
        'public'              => true,
        'has_archive'         => true,
        'menu_icon'           => 'dashicons-money-alt',
        'supports'            => array('title', 'editor', 'thumbnail', 'excerpt', 'custom-fields'),
        'rewrite'             => array('slug' => 'tokens'),
        'show_in_rest'        => true,
        'menu_position'       => 6,
    ));
    
    // Register taxonomies
    register_taxonomy('token_network', 'tec_token', array(
        'labels' => array(
            'name'              => __('Networks', 'tec-theme'),
            'singular_name'     => __('Network', 'tec-theme'),
        ),
        'hierarchical'      => true,
        'public'            => true,
        'show_in_rest'      => true,
        'rewrite'           => array('slug' => 'network'),
    ));
    
    register_taxonomy('faction_alignment', 'tec_faction', array(
        'labels' => array(
            'name'              => __('Alignments', 'tec-theme'),
            'singular_name'     => __('Alignment', 'tec-theme'),
        ),
        'hierarchical'      => true,
        'public'            => true,
        'show_in_rest'      => true,
        'rewrite'           => array('slug' => 'alignment'),
    ));
    
    // Flush rewrite rules only on theme activation
    if (get_option('tec_theme_activation_flush') == 'yes') {
        flush_rewrite_rules();
        delete_option('tec_theme_activation_flush');
    }
}
add_action('init', 'tec_theme_register_post_types');

/**
 * Set the option to flush rewrite rules on activation
 */
function tec_theme_activation() {
    add_option('tec_theme_activation_flush', 'yes');
}
register_activation_hook(__FILE__, 'tec_theme_activation');

/**
 * Register custom REST API endpoints for TEC
 */
function tec_theme_register_rest_routes() {
    register_rest_route('tec/v1', '/factions', array(
        'methods'  => WP_REST_Server::READABLE,
        'callback' => 'tec_theme_get_factions',
        'permission_callback' => '__return_true',
    ));
    
    register_rest_route('tec/v1', '/crypto', array(
        'methods'  => WP_REST_Server::READABLE,
        'callback' => 'tec_theme_get_crypto_data',
        'permission_callback' => '__return_true',
    ));
}
add_action('rest_api_init', 'tec_theme_register_rest_routes');

/**
 * Callback function to get factions data
 * Integrates with our JSON data file
 */
function tec_theme_get_factions() {
    // Path to factions JSON file in the data directory
    $factions_file = ABSPATH . '../data/factions.json';
    
    if (file_exists($factions_file)) {
        $factions_data = json_decode(file_get_contents($factions_file), true);
        return new WP_REST_Response($factions_data, 200);
    } else {
        // Fallback to WordPress factions if JSON file doesn't exist
        $args = array(
            'post_type'      => 'tec_faction',
            'posts_per_page' => -1,
            'post_status'    => 'publish',
        );
        
        $factions = array();
        $query = new WP_Query($args);
        
        if ($query->have_posts()) {
            while ($query->have_posts()) {
                $query->the_post();
                $faction = array(
                    'id'          => get_the_ID(),
                    'name'        => get_the_title(),
                    'description' => get_the_excerpt(),
                    'image'       => get_the_post_thumbnail_url(get_the_ID(), 'full'),
                    'color'       => get_post_meta(get_the_ID(), 'faction_color', true),
                );
                $factions[] = $faction;
            }
            wp_reset_postdata();
        }
        
        return new WP_REST_Response($factions, 200);
    }
}

/**
 * Callback function to get crypto data
 * Integrates with our JSON data file
 */
function tec_theme_get_crypto_data() {
    // Path to wallets JSON file in the data directory
    $wallets_file = ABSPATH . '../data/wallets.json';
    
    if (file_exists($wallets_file)) {
        $wallets_data = json_decode(file_get_contents($wallets_file), true);
        return new WP_REST_Response($wallets_data, 200);
    } else {
        // Fallback to WordPress tokens if JSON file doesn't exist
        $args = array(
            'post_type'      => 'tec_token',
            'posts_per_page' => -1,
            'post_status'    => 'publish',
        );
        
        $tokens = array();
        $query = new WP_Query($args);
        
        if ($query->have_posts()) {
            while ($query->have_posts()) {
                $query->the_post();
                $token = array(
                    'id'          => get_the_ID(),
                    'name'        => get_the_title(),
                    'symbol'      => get_post_meta(get_the_ID(), 'token_symbol', true),
                    'price'       => get_post_meta(get_the_ID(), 'token_price', true),
                    'network'     => get_post_meta(get_the_ID(), 'token_network', true),
                );
                $tokens[] = $token;
            }
            wp_reset_postdata();
        }
        
        return new WP_REST_Response($tokens, 200);
    }
}

/**
 * Include theme features and components
 */
require_once TEC_THEME_DIR . '/inc/template-functions.php';
require_once TEC_THEME_DIR . '/inc/template-tags.php';
require_once TEC_THEME_DIR . '/inc/customizer.php';

/**
 * Integration with ClickUp Agent
 */
function tec_theme_clickup_integration() {
    // Only run this in admin or when specific transients aren't set
    if (is_admin() || (!get_transient('tec_clickup_sync_running') && !wp_doing_ajax())) {
        // Check if the ClickUp agent file exists
        $clickup_agent_file = ABSPATH . '../agents/clickup_agent.py';
        
        if (file_exists($clickup_agent_file)) {
            // Set a transient to prevent multiple syncs
            set_transient('tec_clickup_sync_running', true, 5 * MINUTE_IN_SECONDS);
            
            // Set up the command to run the agent
            $cmd = 'python ' . escapeshellarg($clickup_agent_file) . ' --action=sync_wp';
            
            // Execute the command in the background
            if (function_exists('exec')) {
                exec($cmd . ' > /dev/null 2>&1 &');
            }
        }
    }
}
add_action('init', 'tec_theme_clickup_integration');

/**
 * Create REST API endpoint for TEC Bot to post content
 */
function tec_theme_register_tecbot_endpoint() {
    register_rest_route('tec/v1', '/bot-post', array(
        'methods'  => WP_REST_Server::CREATABLE,
        'callback' => 'tec_theme_handle_bot_post',
        'permission_callback' => 'tec_theme_verify_bot_permissions',
    ));
}
add_action('rest_api_init', 'tec_theme_register_tecbot_endpoint');

/**
 * Verify permissions for TEC Bot
 */
function tec_theme_verify_bot_permissions($request) {
    $api_key = $request->get_header('X-TEC-API-KEY');
    
    // Compare with stored API key (should be stored securely)
    $stored_api_key = get_option('tec_bot_api_key');
    
    return ($api_key === $stored_api_key);
}

/**
 * Handle bot post request
 */
function tec_theme_handle_bot_post($request) {
    $params = $request->get_params();
    
    // Required fields
    if (!isset($params['title']) || !isset($params['content']) || !isset($params['post_type'])) {
        return new WP_Error('missing_fields', 'Required fields are missing', array('status' => 400));
    }
    
    $post_data = array(
        'post_title'    => sanitize_text_field($params['title']),
        'post_content'  => wp_kses_post($params['content']),
        'post_type'     => sanitize_key($params['post_type']),
        'post_status'   => isset($params['status']) ? sanitize_key($params['status']) : 'draft',
    );
    
    // Optional fields
    if (isset($params['excerpt'])) {
        $post_data['post_excerpt'] = sanitize_text_field($params['excerpt']);
    }
    
    // Insert the post
    $post_id = wp_insert_post($post_data);
    
    if (is_wp_error($post_id)) {
        return new WP_Error('post_creation_failed', $post_id->get_error_message(), array('status' => 500));
    }
    
    // Handle featured image if provided
    if (isset($params['featured_image_url'])) {
        $featured_image_url = esc_url_raw($params['featured_image_url']);
        tec_theme_set_featured_image_from_url($post_id, $featured_image_url);
    }
    
    // Handle taxonomy terms if provided
    if (isset($params['terms']) && is_array($params['terms'])) {
        foreach ($params['terms'] as $taxonomy => $terms) {
            wp_set_object_terms($post_id, $terms, sanitize_key($taxonomy));
        }
    }
    
    // Handle custom fields if provided
    if (isset($params['meta']) && is_array($params['meta'])) {
        foreach ($params['meta'] as $meta_key => $meta_value) {
            update_post_meta($post_id, sanitize_key($meta_key), $meta_value);
        }
    }
    
    return new WP_REST_Response(array(
        'success' => true,
        'post_id' => $post_id,
        'permalink' => get_permalink($post_id),
    ), 201);
}

/**
 * Set featured image from URL
 */
function tec_theme_set_featured_image_from_url($post_id, $image_url) {
    // Download image from URL
    $upload = wp_upload_bits(basename($image_url), null, file_get_contents($image_url));
    
    if ($upload['error']) {
        return false;
    }
    
    $file_path = $upload['file'];
    $file_name = basename($file_path);
    $file_type = wp_check_filetype($file_name, null);
    $attachment_title = sanitize_file_name(pathinfo($file_name, PATHINFO_FILENAME));
    
    $attachment = array(
        'post_mime_type' => $file_type['type'],
        'post_title'     => $attachment_title,
        'post_content'   => '',
        'post_status'    => 'inherit',
    );
    
    // Insert attachment
    $attach_id = wp_insert_attachment($attachment, $file_path, $post_id);
    
    // Generate metadata
    require_once(ABSPATH . 'wp-admin/includes/image.php');
    $attach_data = wp_generate_attachment_metadata($attach_id, $file_path);
    wp_update_attachment_metadata($attach_id, $attach_data);
    
    // Set as featured image
    set_post_thumbnail($post_id, $attach_id);
    
    return $attach_id;
}

/**
 * Load TEC Theme template files
 */
function tec_theme_load_template_files() {
    // Create template files directory if it doesn't exist
    $inc_dir = TEC_THEME_DIR . '/inc';
    if (!file_exists($inc_dir)) {
        mkdir($inc_dir, 0755);
    }
    
    // Create template files if they don't exist
    $template_files = array(
        'template-functions.php',
        'template-tags.php',
        'customizer.php',
    );
    
    foreach ($template_files as $file) {
        $file_path = $inc_dir . '/' . $file;
        if (!file_exists($file_path)) {
            file_put_contents($file_path, '<?php' . PHP_EOL . '/**' . PHP_EOL . ' * TEC Theme ' . str_replace('.php', '', $file) . PHP_EOL . ' *' . PHP_EOL . ' * @package TEC_Theme' . PHP_EOL . ' */' . PHP_EOL);
        }
    }
}
add_action('after_setup_theme', 'tec_theme_load_template_files');