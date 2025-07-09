// Test file for frontend hooks - TESTING SEPARATE HOOKS PER FILE TYPE
function testFunction(name,age) {
  if(age<18){
    return `Hello ${name}, you are ${age} years old and under 18`;
  }else{
    return `Hello ${name}, you are ${age} years old and an adult`;
  }
}

// Intentional formatting issues
const x=1+2+3;
const y=[1,2,3,4,5];
const z={name:"test",value:123};

console.log(testFunction("John",25));
