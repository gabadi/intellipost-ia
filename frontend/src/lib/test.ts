/**
 * Test file for frontend tooling validation
 */

export interface TestInterface {
  id: number;
  name: string;
  active: boolean;
}

export const testFunction = (data: TestInterface): string => {
  return `Test item: ${data.name} (${data.active ? 'active' : 'inactive'})`;
};

export const testArray: TestInterface[] = [
  { id: 1, name: 'Test 1', active: true },
  { id: 2, name: 'Test 2', active: false },
];
