use std::env;

fn main() {
    let vulkan_sdk = env::var("VULKAN_SDK").unwrap();
    println!("cargo:rustc-link-search=native={}/lib", vulkan_sdk);
}
