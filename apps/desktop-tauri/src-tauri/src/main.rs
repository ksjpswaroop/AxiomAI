#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use reqwest::Method;
use serde_json::Value;

#[tauri::command]
async fn proxy_json(method: String, url: String, body: Option<Value>) -> Result<Value, String> {
    let method = Method::from_bytes(method.as_bytes()).map_err(|e| format!("invalid method: {e}"))?;
    let client = reqwest::Client::new();

    let mut request = client
        .request(method, url)
        .header("content-type", "application/json");

    if let Some(json_body) = body {
        request = request.json(&json_body);
    }

    let response = request.send().await.map_err(|e| format!("request failed: {e}"))?;
    let status = response.status();
    let text = response
        .text()
        .await
        .map_err(|e| format!("failed to read response: {e}"))?;

    if !status.is_success() {
        return Err(format!("http {}: {}", status.as_u16(), text));
    }

    match serde_json::from_str::<Value>(&text) {
        Ok(v) => Ok(v),
        Err(_) => Ok(serde_json::json!({ "text": text })),
    }
}

fn main() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![proxy_json])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
