    <!-- فوتر سایت -->
    <footer>
        <div class="container">
            <div class="footer-content">
                <div class="footer-column">
                    <?php if ( has_custom_logo() ) : ?>
                        <?php the_custom_logo(); ?>
                    <?php else : ?>
                        <h2 style="color:#fff; margin-bottom: 20px;">RAYNA</h2>
                    <?php endif; ?>
                    <p style="color: #bbb; line-height: 1.8;">فروشگاه RAYNA ارائه‌دهنده جدیدترین و باکیفیت‌ترین لباس‌های مد روز با طراحی‌های خاص و منحصر به فرد.</p>
                    <div class="social-links">
                        <a href="#"><i class="fab fa-instagram"></i></a>
                        <a href="#"><i class="fab fa-twitter"></i></a>
                        <a href="#"><i class="fab fa-telegram"></i></a>
                        <a href="#"><i class="fab fa-linkedin-in"></i></a>
                    </div>
                </div>
                <div class="footer-column">
                    <h4>لینک‌های سریع</h4>
                    <ul>
                        <li><a href="#">درباره ما</a></li>
                        <li><a href="#">تماس با ما</a></li>
                        <li><a href="#">وبلاگ</a></li>
                        <li><a href="#">سوالات متداول</a></li>
                        <li><a href="#">قوانین و مقررات</a></li>
                    </ul>
                </div>
                <div class="footer-column">
                    <h4>دسته‌بندی‌ها</h4>
                    <ul>
                        <li><a href="#">لباس زنانه</a></li>
                        <li><a href="#">لباس مردانه</a></li>
                        <li><a href="#">اکسسوری</a></li>
                        <li><a href="#">کیف و کفش</a></li>
                        <li><a href="#">شال و روسری</a></li>
                    </ul>
                </div>
                <div class="footer-column">
                    <h4>تماس با ما</h4>
                    <div class="contact-item">
                        <i class="fas fa-map-marker-alt"></i>
                        <span>تهران، خیابان ولیعصر، پلاک ۱۲۳</span>
                    </div>
                    <div class="contact-item">
                        <i class="fas fa-phone-alt"></i>
                        <span><?php echo esc_html( get_theme_mod( 'rayna_contact_phone', '۰۲۱-۸۸XXXXXX' ) ); ?></span>
                    </div>
                    <div class="contact-item">
                        <i class="fas fa-envelope"></i>
                        <span>info@rayna.com</span>
                    </div>
                    <h4 style="margin-top: 20px;">عضویت در خبرنامه</h4>
                    <form class="newsletter-form">
                        <input type="email" placeholder="ایمیل خود را وارد کنید">
                        <button type="submit"><i class="fas fa-paper-plane"></i></button>
                    </form>
                </div>
            </div>
            <div class="footer-bottom">
                <p>&copy; <?php echo date('Y'); ?> <?php echo esc_html( get_theme_mod( 'rayna_footer_copy', 'تمامی حقوق برای فروشگاه RAYNA محفوظ است.' ) ); ?></p>
                <div class="payment-logos">
                    <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/5/5b/Visa_Inc._logo.svg/2560px-Visa_Inc._logo.svg.png" alt="Visa">
                    <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/2/2a/Mastercard-logo.svg/1280px-Mastercard-logo.svg.png" alt="Mastercard">
                    <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/e/e1/ZarinPal_logo.svg/2048px-ZarinPal_logo.svg.png" alt="Zarinpal">
                </div>
            </div>
        </div>
    </footer>

    <?php wp_footer(); ?>
</body>
</html>
