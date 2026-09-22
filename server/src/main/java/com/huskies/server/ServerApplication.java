package com.huskies.server;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cache.annotation.EnableCaching;
import org.springframework.context.annotation.Bean;
import org.springframework.web.servlet.config.annotation.CorsRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

@SpringBootApplication
@EnableCaching
public class ServerApplication {

	public static void main(String[] args) {
		SpringApplication.run(ServerApplication.class, args);
	}

	@Bean
	public WebMvcConfigurer corsConfigurer() {
		return new WebMvcConfigurer() {
			@Override
			public void addCorsMappings(CorsRegistry registry) {
				// Read-only public data, no auth or cookies, so credentials mode is
				// unnecessary. Origins stay restricted to the known frontends.
				registry.addMapping("/api/**")
					.allowedOriginPatterns("http://localhost:[*]", "https://zfdupont.com:[*]")
					.maxAge(3600);
			}
		};
	}
}
