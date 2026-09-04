import { BrowserRouter, Routes, Route } from "react-router-dom";
import { Sidebar } from "@/components/Sidebar";
import { Header } from "@/components/Header";
import { ErrorBoundary } from "@/components/ErrorBoundary";
import { Home } from "@/pages/Home";
import { Yields } from "@/pages/Yields";
import { Climate } from "@/pages/Climate";
import { Correlation } from "@/pages/Correlation";
import { ExportCrops } from "@/pages/ExportCrops";
import { Commercialization } from "@/pages/Commercialization";
import { Forecasts } from "@/pages/Forecasts";
import { Map } from "@/pages/Map";
import { Compare } from "@/pages/Compare";
import { About } from "@/pages/About";

export default function App() {
  return (
    <BrowserRouter>
      <div className="flex min-h-screen bg-bg-primary">
        <Sidebar />
        <div className="flex-1 min-w-0 lg:ml-72">
          <Header />
          <main className="min-h-[calc(100vh-64px)]">
            <ErrorBoundary>
              <Routes>
                <Route path="/" element={<Home />} />
                <Route path="/yields" element={<Yields />} />
                <Route path="/climate" element={<Climate />} />
                <Route path="/correlation" element={<Correlation />} />
                <Route path="/export-crops" element={<ExportCrops />} />
                <Route
                  path="/commercialization"
                  element={<Commercialization />}
                />
                <Route path="/forecasts" element={<Forecasts />} />
                <Route path="/map" element={<Map />} />
                <Route path="/compare" element={<Compare />} />
                <Route path="/about" element={<About />} />
              </Routes>
            </ErrorBoundary>
          </main>
        </div>
      </div>
    </BrowserRouter>
  );
}
