use actix_web::{web, App, HttpServer, HttpResponse, Responder};
use serde::{Deserialize, Serialize};
use std::sync::Mutex;
use chrono::{DateTime, Utc};

// --- Modelos ---
#[derive(Serialize, Deserialize, Clone)]
struct Renta {
    id: usize,
    cliente: String,
    dvd_titulo: String,
    staff_id: String,
    costo: f64,
    fecha_renta: DateTime<Utc>,
    devuelto: bool,
}

struct AppState {
    rentas: Mutex<Vec<Renta>>,
}

// --- Handlers (Lógica) ---

// 1. Crear Renta
async fn crear_renta(data: web::Data<AppState>, renta_json: web::Json<Renta>) -> impl Responder {
    let mut rentas = data.rentas.lock().unwrap();
    let mut nueva_renta = renta_json.into_inner();
    nueva_renta.id = rentas.len() + 1; // ID simple
    nueva_renta.fecha_renta = Utc::now();
    nueva_renta.devuelto = false;
    
    rentas.push(nueva_renta);
    HttpResponse::Created().json("Renta creada exitosamente")
}

// 2. Devolver DVD
async fn devolver_dvd(data: web::Data<AppState>, id: web::Path<usize>) -> impl Responder {
    let mut rentas = data.rentas.lock().unwrap();
    if let Some(renta) = rentas.iter_mut().find(|r| r.id == *id) {
        renta.devuelto = true;
        HttpResponse::Ok().json(format!("DVD '{}' devuelto", renta.dvd_titulo))
    } else {
        HttpResponse::NotFound().json("Renta no encontrada")
    }
}

// 3. Cancelar Renta (Eliminar)
async fn cancelar_renta(data: web::Data<AppState>, id: web::Path<usize>) -> impl Responder {
    let mut rentas = data.rentas.lock().unwrap();
    let len_inicial = rentas.len();
    rentas.retain(|r| r.id != *id);
    
    if rentas.len() < len_inicial {
        HttpResponse::Ok().json("Renta cancelada y eliminada")
    } else {
        HttpResponse::NotFound().json("Renta no encontrada")
    }
}

// --- Reportes ---

// Reporte A: Lista de rentas de un cliente
async fn reporte_cliente(data: web::Data<AppState>, cliente: web::Path<String>) -> impl Responder {
    let rentas = data.rentas.lock().unwrap();
    let resultado: Vec<&Renta> = rentas.iter().filter(|r| r.cliente == *cliente).collect();
    HttpResponse::Ok().json(resultado)
}

// Reporte B: DVDs no devueltos
async fn reporte_pendientes(data: web::Data<AppState>) -> impl Responder {
    let rentas = data.rentas.lock().unwrap();
    let resultado: Vec<&Renta> = rentas.iter().filter(|r| !r.devuelto).collect();
    HttpResponse::Ok().json(resultado)
}

// Reporte C: DVDs más rentados (Conteo simple)
async fn reporte_populares(data: web::Data<AppState>) -> impl Responder {
    let rentas = data.rentas.lock().unwrap();
    // En una DB real usaríamos SQL GROUP BY. Aquí simplificamos devolviendo todo para procesar o contar
    // Para el ejemplo, devolvemos la lista completa, el frontend puede contar.
    HttpResponse::Ok().json(&*rentas) 
}

// Reporte D: Ganancia por Staff
async fn reporte_staff_ganancia(data: web::Data<AppState>) -> impl Responder {
    let rentas = data.rentas.lock().unwrap();
    // Retornamos todas las rentas, el cálculo se puede hacer aquí o en front. Haremos un resumen simple aquí.
    // Nota: Para una API REST pura, idealmente devolveríamos un JSON pre-calculado { "staff_a": 100, "staff_b": 200 }
    // Por simplicidad, devolvemos todas las rentas.
    HttpResponse::Ok().json(&*rentas)
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    let data = web::Data::new(AppState {
        rentas: Mutex::new(vec![]),
    });

    println!("Servidor corriendo en http://0.0.0.0:8080");

    HttpServer::new(move || {
        App::new()
            .app_data(data.clone())
            .route("/rentar", web::post().to(crear_renta))
            .route("/devolver/{id}", web::put().to(devolver_dvd))
            .route("/cancelar/{id}", web::delete().to(cancelar_renta))
            .route("/reporte/cliente/{nombre}", web::get().to(reporte_cliente))
            .route("/reporte/pendientes", web::get().to(reporte_pendientes))
            .route("/reporte/general", web::get().to(reporte_staff_ganancia)) // Usado para populares y ganancias
    })
    .bind(("0.0.0.0", 8080))?
    .run()
    .await
}