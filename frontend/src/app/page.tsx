// 'use client';

import { Card } from "@/components/Card";
import { Divider } from "@/components/Divider";
import { SelectNative } from "@/components/SelectNative";

function ContentPlaceholder() {
  return (
    <div className="relative h-full overflow-hidden rounded bg-gray-50 dark:bg-gray-800">
      <svg
        className="absolute inset-0 h-full w-full stroke-gray-200 dark:stroke-gray-700"
        fill="none"
      >
        <defs>
          <pattern
            id="pattern-2"
            x="0"
            y="0"
            width="10"
            height="10"
            patternUnits="userSpaceOnUse"
          >
            <path d="M-3 13 15-5M-5 5l18-18M-1 21 17 3"></path>
          </pattern>
        </defs>
        <rect
          stroke="none"
          fill="url(#pattern-2)"
          width="100%"
          height="100%"
        ></rect>
      </svg>
    </div>
  );
}

export default function Example() {
  return (
    <>
      <div className="p-4 sm:p-6 lg:p-8">
        <header>
          <div className="sm:flex sm:items-center sm:justify-between">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-50">
              Report
            </h3>
            <div className="mt-4 flex flex-col gap-2 sm:mt-0 sm:flex-row sm:items-center">
              <SelectNative defaultValue="1">
                <option value="1">Today</option>
                <option value="2">Last 7 days</option>
                <option value="3">Last 4 weeks</option>
                <option value="4">Last 12 months</option>
              </SelectNative>
              <SelectNative defaultValue="1">
                <option value="1">US-West</option>
                <option value="2">US-East</option>
                <option value="3">EU-Central-1</option>
              </SelectNative>
            </div>
          </div>
        </header>
        <Divider />
        <main>
          <Card className="p-0">
            <div className="grid-cols-12 divide-y divide-gray-200 dark:divide-gray-800 md:grid md:divide-x md:divide-y-0">
              <div className="divide-y divide-gray-200 px-2 dark:divide-gray-800 md:col-span-4">
                <div className="h-28 py-2">
                  <ContentPlaceholder />
                </div>
                <div className="h-28 py-2">
                  <ContentPlaceholder />
                </div>
                <div className="h-28 py-2">
                  <ContentPlaceholder />
                </div>
              </div>
              <div className="h-56 p-2 md:col-span-8 md:h-auto">
                <ContentPlaceholder />
              </div>
            </div>
          </Card>
          <dl className="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-2">
            <Card className="p-0">
              <div className="border-b border-gray-200 px-4 py-2 dark:border-gray-800">
                <dt className="text-sm font-medium text-gray-900 dark:text-gray-50">
                  Title
                </dt>
              </div>
              <div className="h-60 p-2">
                <ContentPlaceholder />
              </div>
            </Card>
            <Card className="p-0">
              <div className="border-b border-gray-200 px-4 py-2 dark:border-gray-800">
                <dt className="text-sm font-medium text-gray-900 dark:text-gray-50">
                  Title
                </dt>
              </div>
              <div className="h-60 p-2">
                <ContentPlaceholder />
              </div>
            </Card>
            <Card className="p-0">
              <div className="border-b border-gray-200 px-4 py-2 dark:border-gray-800">
                <dt className="text-sm font-medium text-gray-900 dark:text-gray-50">
                  Title
                </dt>
              </div>
              <div className="h-60 p-2">
                <ContentPlaceholder />
              </div>
            </Card>
            <Card className="p-0">
              <div className="border-b border-gray-200 px-4 py-2 dark:border-gray-800">
                <dt className="text-sm font-medium text-gray-900 dark:text-gray-50">
                  Title
                </dt>
              </div>
              <div className="h-60 p-2">
                <ContentPlaceholder />
              </div>
            </Card>
          </dl>
        </main>
      </div>
    </>
  );
}
