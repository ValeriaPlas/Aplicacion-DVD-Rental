# Usamos una imagen oficial de Rust
FROM rust:1.75 as builder
WORKDIR /app
COPY . .
RUN cargo build --release

# Imagen ligera para ejecutar
FROM debian:bookworm-slim
WORKDIR /app
COPY --from=builder /app/target/release/backend_dvd .
EXPOSE 8080
CMD ["./backend_dvd"]