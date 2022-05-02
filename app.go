package main

import (
	"flag"

	"analyze.api/app/handlers"
	_ "analyze.api/docs"

	swagger "github.com/arsmn/fiber-swagger/v2"
	"github.com/gofiber/fiber/v2"
	"github.com/gofiber/fiber/v2/middleware/cors"
)

var (
	port       = flag.String("port", ":3001", "Port to listen on")
	prod       = flag.Bool("prod", true, "Enable prefork in Production")
	staticFile = flag.String("d", "./asset/front/", "static web folder")
)

func setupRoutes(app *fiber.App) {
	apiGroup := app.Group("/api")
	apiGroup.Post("/upload", handlers.FilterData)
	apiGroup.Put("/export", handlers.Export)
	apiGroup.Put("/concat", handlers.Concat)
	apiGroup.Patch("/save", handlers.SaveRange)

	fileGroup := app.Group("/file")
	fileGroup.Static("/csv", "./file/csv/")
	fileGroup.Static("/export", "./file/export/")
	fileGroup.Static("/raw", "./file/raw/")
	fileGroup.Static("/cleaning", "./file/cleaning/")

	app.Get("/swagger/*", swagger.HandlerDefault)
}

func NewServer() *fiber.App {
	app := fiber.New(fiber.Config{
		BodyLimit: 100 * 1024 * 1024, // 100 mb
		Prefork:   *prod,
	})
	app.Use(cors.New(cors.Config{
		AllowOrigins: "http://localhost:3000", // cross origin
	}))

	setupRoutes(app)

	app.Static("/", *staticFile) // if serve static web

	return app
}

// @title           analyze API
// @version         1.0
// @description     analyze python backend
// @termsOfService  http://swagger.io/terms/

// @tag.name         Python
// @tag.description  running python process api

// @contact.name   Wesley
// @contact.email  wesley.ch3n.0530@gmail.com

// @license.name  Apache 2.0
// @license.url   http://www.apache.org/licenses/LICENSE-2.0.html

// @host      localhost:3001
// @BasePath  /
func main() {
	flag.Parse()

	app := NewServer()
	app.Listen(*port)
}
