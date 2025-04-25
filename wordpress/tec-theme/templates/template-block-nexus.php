<?php
/**
 * Template Name: TEC3 Block-Nexus
 * Description: A template for the Block-Nexus page with code box support
 *
 * @package TEC_Theme
 */

get_header();
?>

<main id="primary" class="site-main block-nexus-page">
    <div class="container">
        <article id="post-<?php the_ID(); ?>" <?php post_class(); ?>>
            <header class="entry-header">
                <h1 class="entry-title"><?php the_title(); ?></h1>
            </header>

            <div class="entry-content block-nexus-content">
                <?php the_content(); ?>
                
                <div class="code-boxes-section">
                    <h2>Blockchain Network Data</h2>
                    
                    <div class="code-box ethereum">
                        <h3>Ethereum Network</h3>
                        <pre><code class="language-json"><?php 
                            // Load wallets data from JSON file
                            $wallets_file = dirname(get_stylesheet_directory()) . '/../data/wallets.json';
                            if (file_exists($wallets_file)) {
                                $wallets_data = json_decode(file_get_contents($wallets_file), true);
                                $eth_wallets = array_filter($wallets_data['wallets'], function($wallet) {
                                    return $wallet['chain'] === 'ethereum';
                                });
                                echo json_encode($eth_wallets, JSON_PRETTY_PRINT);
                            } else {
                                echo "Wallet data not available";
                            }
                        ?></code></pre>
                    </div>
                    
                    <div class="code-box xrp">
                        <h3>XRP Network</h3>
                        <pre><code class="language-json"><?php 
                            // Load wallets data for XRP
                            if (isset($wallets_data)) {
                                $xrp_wallets = array_filter($wallets_data['wallets'], function($wallet) {
                                    return $wallet['chain'] === 'xrp';
                                });
                                echo json_encode($xrp_wallets, JSON_PRETTY_PRINT);
                            } else {
                                echo "XRP wallet data not available";
                            }
                        ?></code></pre>
                    </div>
                    
                    <div class="code-box cardano">
                        <h3>Cardano Network</h3>
                        <pre><code class="language-json"><?php 
                            // Load wallets data for Cardano
                            if (isset($wallets_data)) {
                                $ada_wallets = array_filter($wallets_data['wallets'], function($wallet) {
                                    return $wallet['chain'] === 'cardano';
                                });
                                echo json_encode($ada_wallets, JSON_PRETTY_PRINT);
                            } else {
                                echo "Cardano wallet data not available";
                            }
                        ?></code></pre>
                    </div>
                </div>
                
                <div class="bot-integration-section">
                    <h2>TECBot Integration</h2>
                    <?php 
                    // Check if the bot has generated any data
                    $bot_data_file = dirname(get_stylesheet_directory()) . '/../data/bot_output.json';
                    if (file_exists($bot_data_file)) {
                        $bot_data = json_decode(file_get_contents($bot_data_file), true);
                        if (!empty($bot_data)) {
                            echo '<div class="tecbot-data">';
                            echo '<pre><code class="language-json">' . json_encode($bot_data, JSON_PRETTY_PRINT) . '</code></pre>';
                            echo '</div>';
                        } else {
                            echo '<p>No bot data available at this time.</p>';
                        }
                    } else {
                        echo '<p>Bot integration is configured but no data output file exists yet.</p>';
                        echo '<p>The bot will automatically generate data based on blockchain activity.</p>';
                    }
                    ?>
                </div>
            </div>
        </article>
    </div>
</main>

<?php
get_footer();