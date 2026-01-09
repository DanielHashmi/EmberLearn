"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { motion } from "framer-motion";
import { ThemeToggle } from "@/components/shared/theme-toggle";
import { Button } from "@/components/ui/button";

const navItems = [
  { name: "Home", href: "/" },
  { name: "Chat", href: "/chat" },
  { name: "Practice", href: "/practice/basic-syntax" }, // Example default
];

export function NavHeader() {
  const pathname = usePathname();

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 p-6 flex justify-between items-center bg-glass/5 backdrop-blur-sm border-b border-glass-border/10 transition-all duration-300">
      <Link href="/">
        <div className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-primary-500 to-purple-600">
          EmberLearn
        </div>
      </Link>

      <div className="hidden md:flex items-center gap-1 bg-glass/20 p-1.5 rounded-full border border-glass-border/20 backdrop-blur-md shadow-lg shadow-black/5">
        {navItems.map((item) => {
          const isActive = pathname === item.href || (item.href !== "/" && pathname.startsWith(item.href));
          return (
            <Link key={item.href} href={item.href} className="relative">
              {isActive && (
                <motion.div
                  layoutId="nav-pill"
                  className="absolute inset-0 bg-white/10 dark:bg-white/10 rounded-full"
                  transition={{ type: "spring", stiffness: 300, damping: 30 }}
                />
              )}
              <span className={`relative z-10 block px-4 py-2 text-sm font-medium transition-colors duration-200 ${isActive ? "text-foreground" : "text-muted-foreground hover:text-foreground"}`}>
                {item.name}
              </span>
            </Link>
          );
        })}
      </div>

      <div className="flex items-center gap-4">
        <ThemeToggle />
        <Link href="/login">
          <Button variant="ghost" size="sm" className="hover:bg-glass/20">Sign In</Button>
        </Link>
        <Link href="/register">
           <Button size="sm" className="shadow-lg shadow-primary/20">Get Started</Button>
        </Link>
      </div>
    </nav>
  );
}
